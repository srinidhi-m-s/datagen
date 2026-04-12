/**
 * Data Generation AI Platform - Frontend JavaScript
 * With Schema Mapping, Filtering, and Performance Comparison
 */

// API Configuration
const API_BASE_URL = '';

// DOM Elements
const queryInput = document.getElementById('queryInput');
const generateBtn = document.getElementById('generateBtn');
const compareBtn = document.getElementById('compareBtn');
const useKaggleCheckbox = document.getElementById('useKaggle');
const useRAGCheckbox = document.getElementById('useRAG');
const enhancedModeCheckbox = document.getElementById('enhancedMode');
const loadingSection = document.getElementById('loadingSection');
const errorSection = document.getElementById('errorSection');
const errorMessage = document.getElementById('errorMessage');
const resultsSection = document.getElementById('resultsSection');
const comparisonSection = document.getElementById('comparisonSection');
const recordCount = document.getElementById('recordCount');
const schemaInfo = document.getElementById('schemaInfo');
const dataTable = document.getElementById('dataTable');
const downloadCSV = document.getElementById('downloadCSV');
const downloadJSON = document.getElementById('downloadJSON');
const exampleQueries = document.querySelectorAll('.example-query');

// State
let currentData = null;
let comparisonData = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Add event listeners
    generateBtn?.addEventListener('click', handleGenerate);
    compareBtn?.addEventListener('click', handleCompare);
    downloadCSV?.addEventListener('click', handleDownloadCSV);
    downloadJSON?.addEventListener('click', handleDownloadJSON);

    // Example query clicks
    exampleQueries.forEach(query => {
        query.addEventListener('click', () => {
            queryInput.value = query.textContent;
            queryInput.focus();
        });
    });

    // Enter key to generate
    queryInput?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleGenerateSchema();
        }
    });
});

// Generate Schema (NEW FLOW: LLM → Schema Mapper)
async function handleGenerateSchema() {
    const query = queryInput.value.trim();

    if (!query) {
        showError('Please enter a data generation query');
        return;
    }

    hideError();
    hideResults();
    hideComparison();
    showLoading();

    try {
        const response = await fetch(`${API_BASE_URL}/api/generate-schema`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: query,
                use_kaggle: useKaggleCheckbox?.checked || false,
                use_rag: useRAGCheckbox?.checked || false
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to generate schema');
        }

        const result = await response.json();

        if (!result.success) {
            throw new Error(result.error || 'Schema generation failed');
        }

        // Display schema flow
        displaySchemaFlow(result);

    } catch (error) {
        console.error('Schema generation error:', error);
        showError(error.message || 'An unexpected error occurred. Please check your API key and try again.');
    } finally {
        hideLoading();
    }
}


// Generate Data
async function handleGenerate() {
    const query = queryInput.value.trim();

    if (!query) {
        showError('Please enter a data generation query');
        return;
    }

    hideError();
    hideResults();
    hideComparison();
    showLoading();

    try {
        const response = await fetch(`${API_BASE_URL}/api/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: query,
                use_kaggle: useKaggleCheckbox?.checked || false,
                use_rag: useRAGCheckbox?.checked || false,
                enhanced_mode: enhancedModeCheckbox?.checked !== false
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to generate data');
        }

        const result = await response.json();

        if (!result.success) {
            throw new Error(result.error || 'Data generation failed');
        }

        currentData = result;
        displayResults(result);

    } catch (error) {
        console.error('Generation error:', error);
        showError(error.message || 'An unexpected error occurred. Please check your API key and try again.');
    } finally {
        hideLoading();
    }
}

// Compare Modes
async function handleCompare() {
    const query = queryInput.value.trim();

    if (!query) {
        showError('Please enter a data generation query');
        return;
    }

    hideError();
    hideResults();
    hideComparison();
    showLoading();

    try {
        const response = await fetch(`${API_BASE_URL}/api/compare`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: query,
                use_kaggle: useKaggleCheckbox?.checked || false,
                use_rag: useRAGCheckbox?.checked || false
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to compare modes');
        }

        const result = await response.json();

        comparisonData = result;
        displayComparison(result);

        // Also show enhanced result as main data
        if (result.enhanced_result?.success) {
            currentData = result.enhanced_result;
            displayResults(result.enhanced_result);
        }

    } catch (error) {
        console.error('Comparison error:', error);
        showError(error.message || 'An unexpected error occurred.');
    } finally {
        hideLoading();
    }
}

// Display Results
function displayResults(result) {
    const data = result.data;

    if (!data || data.length === 0) {
        showError('No data generated. Try a more specific query.');
        return;
    }

    // Show record count and mode
    const modeLabel = result.mode === 'enhanced' ? '🚀 Enhanced Mode' : '📝 Normal Mode';
    recordCount.textContent = `${data.length} records generated (${modeLabel})`;

    // Show schema with analysis
    displaySchema(result.schema, result.schema_analysis);

    // Show metrics if available
    if (result.metrics) {
        displayMetrics(result.metrics);
    }

    // Display data table
    displayTable(data);

    // Show validation if available
    if (result.validation) {
        displayValidation(result.validation);
    }

    resultsSection.classList.remove('hidden');
}

// Display Schema
function displaySchema(schema, analysis) {
    let html = '<strong>Schema:</strong> ';

    const schemaItems = Object.entries(schema).map(([key, type]) => {
        let fieldType = analysis?.field_types?.[key] || type;
        let badge = '';
        if (fieldType === 'id') badge = '🔑';
        else if (fieldType === 'email') badge = '📧';
        else if (fieldType === 'name') badge = '👤';
        else if (fieldType === 'price') badge = '💰';
        else if (fieldType === 'date') badge = '📅';
        else if (fieldType === 'location') badge = '📍';

        return `<span class="schema-item">${badge} ${key}: ${type}</span>`;
    });

    html += schemaItems.join(' | ');

    // Add relationships if available
    if (analysis?.relationships?.length > 0) {
        html += '<br><br><strong>Semantic Relationships:</strong><ul class="relationships-list">';
        analysis.relationships.forEach(rel => {
            html += `<li>📊 ${rel}</li>`;
        });
        html += '</ul>';
    }

    schemaInfo.innerHTML = html;
}

// Display Metrics
function displayMetrics(metrics) {
    let metricsContainer = document.getElementById('metricsContainer');

    if (!metricsContainer) {
        metricsContainer = document.createElement('div');
        metricsContainer.id = 'metricsContainer';
        metricsContainer.className = 'metrics-container';
        schemaInfo.parentNode.insertBefore(metricsContainer, schemaInfo.nextSibling);
    }

    metricsContainer.innerHTML = `
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">${metrics.response_time_ms?.toFixed(0) || 0}ms</div>
                <div class="metric-label">Response Time</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${metrics.schema_compliance?.toFixed(1) || 0}%</div>
                <div class="metric-label">Schema Compliance</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${metrics.relationship_score?.toFixed(1) || 0}%</div>
                <div class="metric-label">Relationship Score</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${metrics.data_quality_score?.toFixed(1) || 0}%</div>
                <div class="metric-label">Data Quality</div>
            </div>
            <div class="metric-card highlight">
                <div class="metric-value">${metrics.overall_score?.toFixed(1) || 0}%</div>
                <div class="metric-label">Overall Score</div>
            </div>
        </div>
    `;
}

// Display Validation
function displayValidation(validation) {
    let validationContainer = document.getElementById('validationContainer');

    if (!validationContainer) {
        validationContainer = document.createElement('div');
        validationContainer.id = 'validationContainer';
        validationContainer.className = 'validation-container';
        const metricsContainer = document.getElementById('metricsContainer');
        if (metricsContainer) {
            metricsContainer.parentNode.insertBefore(validationContainer, metricsContainer.nextSibling);
        }
    }

    const qualityClass = validation.quality_score >= 80 ? 'good' :
        validation.quality_score >= 50 ? 'medium' : 'poor';

    validationContainer.innerHTML = `
        <div class="validation-summary ${qualityClass}">
            <span class="validation-icon">${validation.quality_score >= 80 ? '✅' : validation.quality_score >= 50 ? '⚠️' : '❌'}</span>
            <span>Data Quality: ${validation.quality_score?.toFixed(1)}%</span>
            <span class="validation-details">
                ${validation.valid_records}/${validation.total_records} valid records
            </span>
        </div>
    `;
}

// Display Comparison
function displayComparison(result) {
    if (!comparisonSection) return;

    const comparison = result.comparison;
    if (!comparison) return;

    const improvements = comparison.improvements;

    comparisonSection.innerHTML = `
        <h3>📊 Performance Comparison: Normal vs Enhanced Mode</h3>
        
        <div class="comparison-grid">
            <div class="comparison-card normal">
                <h4>📝 Normal Mode</h4>
                <div class="comparison-stats">
                    <div class="stat">
                        <span class="stat-label">Response Time</span>
                        <span class="stat-value">${comparison.normal_mode.response_time_ms?.toFixed(0)}ms</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Schema Compliance</span>
                        <span class="stat-value">${comparison.normal_mode.schema_compliance?.toFixed(1)}%</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Relationship Score</span>
                        <span class="stat-value">${comparison.normal_mode.relationship_score?.toFixed(1)}%</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Data Quality</span>
                        <span class="stat-value">${comparison.normal_mode.data_quality_score?.toFixed(1)}%</span>
                    </div>
                    <div class="stat overall">
                        <span class="stat-label">Overall Score</span>
                        <span class="stat-value">${comparison.normal_mode.overall_score?.toFixed(1)}%</span>
                    </div>
                </div>
            </div>
            
            <div class="comparison-arrow">
                <span class="arrow">→</span>
                <span class="improvement ${improvements.overall.improvement_percent > 0 ? 'positive' : 'negative'}">
                    ${improvements.overall.improvement_percent > 0 ? '+' : ''}${improvements.overall.improvement_percent?.toFixed(1)}%
                </span>
            </div>
            
            <div class="comparison-card enhanced">
                <h4>🚀 Enhanced Mode</h4>
                <div class="comparison-stats">
                    <div class="stat">
                        <span class="stat-label">Response Time</span>
                        <span class="stat-value">${comparison.enhanced_mode.response_time_ms?.toFixed(0)}ms</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Schema Compliance</span>
                        <span class="stat-value">${comparison.enhanced_mode.schema_compliance?.toFixed(1)}%</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Relationship Score</span>
                        <span class="stat-value">${comparison.enhanced_mode.relationship_score?.toFixed(1)}%</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Data Quality</span>
                        <span class="stat-value">${comparison.enhanced_mode.data_quality_score?.toFixed(1)}%</span>
                    </div>
                    <div class="stat overall">
                        <span class="stat-label">Overall Score</span>
                        <span class="stat-value">${comparison.enhanced_mode.overall_score?.toFixed(1)}%</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="comparison-summary">
            <h4>🎯 Key Benefits of Enhanced Mode</h4>
            <ul class="benefits-list">
                ${comparison.summary.key_benefits.map(b => `<li>✅ ${b}</li>`).join('')}
            </ul>
        </div>
    `;

    comparisonSection.classList.remove('hidden');
}

// Display Schema Flow (LLM → Schema Mapper)
function displaySchemaFlow(result) {
    if (!resultsSection) return;

    const llmOutput = result.llm_raw_output;
    const validatedSchema = result.schema;
    const metadata = result.metadata;

    // Create schema flow display
    const schemaFlowHTML = `
        <div class="schema-flow-container">
            <h3>🔄 Schema Generation Flow</h3>
            <p class="flow-description">Query: "${result.query}"</p>
            
            <div class="flow-steps">
                <!-- Step 1: LLM Output -->
                <div class="flow-step">
                    <div class="step-header">
                        <span class="step-number">1</span>
                        <h4>🤖 LLM Schema Extraction</h4>
                    </div>
                    <div class="step-content">
                        <p class="step-description">The LLM analyzes your query and generates a comprehensive schema with semantic understanding.</p>
                        <div class="json-display">
                            <div class="json-header">
                                <span>Raw LLM Output</span>
                                <button class="copy-btn" onclick="copyToClipboard('llm-output')">📋 Copy</button>
                            </div>
                            <pre id="llm-output"><code>${JSON.stringify(llmOutput, null, 2)}</code></pre>
                        </div>
                        <div class="schema-summary">
                            <div class="summary-item">
                                <span class="label">Dataset:</span>
                                <span class="value">${llmOutput.dataset_name}</span>
                            </div>
                            <div class="summary-item">
                                <span class="label">Rows:</span>
                                <span class="value">${llmOutput.rows}</span>
                            </div>
                            <div class="summary-item">
                                <span class="label">Columns:</span>
                                <span class="value">${llmOutput.columns?.length || 0}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Arrow -->
                <div class="flow-arrow">
                    <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
                        <path d="M20 5 L20 30 M20 30 L15 25 M20 30 L25 25" stroke="#667eea" stroke-width="2" fill="none"/>
                    </svg>
                    <span>Validation & Normalization</span>
                </div>

                <!-- Step 2: Schema Mapper Output -->
                <div class="flow-step">
                    <div class="step-header">
                        <span class="step-number">2</span>
                        <h4>🔍 Schema Mapper Validation</h4>
                    </div>
                    <div class="step-content">
                        <p class="step-description">The schema mapper validates and normalizes the LLM output into a type-safe, structured schema.</p>
                        <div class="json-display">
                            <div class="json-header">
                                <span>Validated Schema</span>
                                <button class="copy-btn" onclick="copyToClipboard('validated-schema')">📋 Copy</button>
                            </div>
                            <pre id="validated-schema"><code>${JSON.stringify(validatedSchema, null, 2)}</code></pre>
                        </div>
                        <div class="schema-summary success">
                            <div class="summary-item">
                                <span class="label">✅ Dataset:</span>
                                <span class="value">${metadata.dataset_name}</span>
                            </div>
                            <div class="summary-item">
                                <span class="label">✅ Rows:</span>
                                <span class="value">${metadata.rows}</span>
                            </div>
                            <div class="summary-item">
                                <span class="label">✅ Columns:</span>
                                <span class="value">${metadata.column_count}</span>
                            </div>
                            <div class="summary-item">
                                <span class="label">✅ Version:</span>
                                <span class="value">${metadata.version}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Transformation Comparison -->
                <div class="transformation-section">
                    <h4>🔄 Type Transformations</h4>
                    <table class="transformation-table">
                        <thead>
                            <tr>
                                <th>Column Name</th>
                                <th>LLM Type</th>
                                <th>→</th>
                                <th>Normalized Type</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${llmOutput.columns?.map((llmCol, idx) => {
        const schemaCol = validatedSchema.columns[idx];
        return `
                                    <tr>
                                        <td><strong>${llmCol.name}</strong></td>
                                        <td><code>${llmCol.type}</code></td>
                                        <td>→</td>
                                        <td><code class="normalized">${schemaCol.type}</code></td>
                                    </tr>
                                `;
    }).join('')}
                        </tbody>
                    </table>
                </div>

                <!-- Final Status -->
                <div class="flow-result">
                    <div class="result-icon">✅</div>
                    <h4>Schema Validated Successfully!</h4>
                    <p>This validated schema is ready for:</p>
                    <ul>
                        <li>✓ RAG processing and Kaggle dataset matching</li>
                        <li>✓ Data generation with type safety</li>
                        <li>✓ Storage and caching</li>
                        <li>✓ Further validation and filtering</li>
                    </ul>
                </div>
            </div>
        </div>
    `;

    // Show in results section
    resultsSection.innerHTML = `
        <div class="card results-card">
            ${schemaFlowHTML}
        </div>
    `;
    resultsSection.classList.remove('hidden');
}

// Copy to clipboard helper
function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;

    const text = element.textContent;
    navigator.clipboard.writeText(text).then(() => {
        // Show feedback
        const btn = event.target;
        const originalText = btn.textContent;
        btn.textContent = '✅ Copied!';
        setTimeout(() => {
            btn.textContent = originalText;
        }, 2000);
    });
}


// Display Data Table
function displayTable(data) {
    if (!data || data.length === 0) {
        dataTable.innerHTML = '<p>No data to display</p>';
        return;
    }

    const headers = Object.keys(data[0]);

    let html = '<table class="data-table"><thead><tr>';
    headers.forEach(header => {
        html += `<th>${header}</th>`;
    });
    html += '</tr></thead><tbody>';

    data.forEach((row, index) => {
        html += `<tr class="${index % 2 === 0 ? 'even' : 'odd'}">`;
        headers.forEach(header => {
            const value = row[header];
            const displayValue = typeof value === 'object' ? JSON.stringify(value) : value;
            html += `<td>${displayValue ?? ''}</td>`;
        });
        html += '</tr>';
    });

    html += '</tbody></table>';
    dataTable.innerHTML = html;
}

// Download handlers
function handleDownloadCSV() {
    if (!currentData?.data) {
        showError('No data to download');
        return;
    }

    const data = currentData.data;
    const headers = Object.keys(data[0]);

    let csv = headers.join(',') + '\n';
    data.forEach(row => {
        const values = headers.map(h => {
            const value = row[h];
            if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
                return `"${value.replace(/"/g, '""')}"`;
            }
            return value ?? '';
        });
        csv += values.join(',') + '\n';
    });

    downloadFile(csv, 'generated_data.csv', 'text/csv');
}

function handleDownloadJSON() {
    if (!currentData?.data) {
        showError('No data to download');
        return;
    }

    const json = JSON.stringify(currentData.data, null, 2);
    downloadFile(json, 'generated_data.json', 'application/json');
}

function downloadFile(content, filename, type) {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// UI Helpers
function showLoading() {
    loadingSection?.classList.remove('hidden');
}

function hideLoading() {
    loadingSection?.classList.add('hidden');
}

function showError(message) {
    if (errorSection && errorMessage) {
        errorMessage.textContent = message;
        errorSection.classList.remove('hidden');
    }
}

function hideError() {
    errorSection?.classList.add('hidden');
}

function hideResults() {
    resultsSection?.classList.add('hidden');

    // Clear metrics and validation containers
    const metricsContainer = document.getElementById('metricsContainer');
    const validationContainer = document.getElementById('validationContainer');
    if (metricsContainer) metricsContainer.remove();
    if (validationContainer) validationContainer.remove();
}

function hideComparison() {
    comparisonSection?.classList.add('hidden');
}
