
/**
 * CONSULTANCY OS - ENTERPRISE ENGINE v4.1
 * Core Logic: Navigation, Form Building, and Add New Integrity
 */
const engine = {
    currentDoctype: null,
    meta: null,
    data: [],

    async navigate() {
        const hash = window.location.hash.replace('#', '');
        const parts = hash.split('/');
        const doctype = parts[0] || 'Dashboard';
        const mode = parts[1] || 'list';
        const id = parts[2] || null;

        this.currentDoctype = doctype;

        // UI Navigation Update
        $('.active-nav').removeClass('active-nav bg-primary-50 text-primary-600').addClass('text-gray-700 font-medium');
        $(`a[href="#${doctype}"]`).addClass('active-nav bg-primary-50 text-primary-600').removeClass('text-gray-700 font-medium');
        $('#current-page-label').text(doctype.replace(/_/g, ' '));

        if (doctype === 'Dashboard') {
            await this.renderDashboard();
            return;
        }

        if (doctype === 'Settings') {
            await this.renderSettingsPage();
            return;
        }

        if (mode === 'Form' || mode === 'Edit') {
            await this.renderFormPage(id);
        } else {
            await this.refreshList();
        }
    },

    async refreshList(search = '') {
        ui.setLoading(true);
        try {
            const pageName = this.currentDoctype.toLowerCase();
            const template = await fetch(`/portal/pages/${pageName}.html`)
                .then(r => r.ok ? r.text() : fetch('/portal/pages/list.html').then(res => res.text()));

            $('#app-viewport').html(template);

            const [meta, data] = await Promise.all([
                api.getMeta(this.currentDoctype),
                api.getList(this.currentDoctype, search)
            ]);
            this.meta = meta;
            this.data = data;
            this.meta = meta;
            this.data = data;

            // NEW: Detect if we are on a specialized dashboard page and need to render its specific visuals
            if ($('#chart-client-types').length > 0) await this.renderClientsDashboard(data);
            if ($('#chart-consultant-status').length > 0) await this.renderConsultantsDashboard(data);
            if ($('#chart-priority').length > 0) await this.renderAssignmentsDashboard(data);
            if ($('#chart-task-completion').length > 0) await this.renderTasksDashboard(data);

            // ACTION BAR INJECTION
            // Ensure the main action bar has the Export button
            const actionContainer = $('#page-action-container');
            if (actionContainer.length > 0 && $('#btn-export-csv').length === 0) {
                actionContainer.prepend(`<button id="btn-export-csv" onclick="engine.exportToCSV()" class="px-6 py-3 text-primary-600 font-bold hover:bg-white rounded-xl transition-colors border border-transparent hover:border-gray-100 hover:shadow-sm">Export CSV</button>`);
            }

            // Bind "Add New" Button Globally - respect permissions
            if (window.userPermissions && window.userPermissions.canCreate) {
                $('.btn-new-entity').off('click').on('click', () => {
                    window.location.hash = `${this.currentDoctype}/Form`;
                }).removeClass('hidden');
            } else {
                $('.btn-new-entity').addClass('hidden');
            }

            // Default fallback or grid renderer for cards/tables
            if ($('#card-grid').length > 0) {
                this.renderCardGrid();
            } else {
                this.renderDataGrid();
            }
        } catch (e) {
            ui.toast("Module Connection Failed", "error");
        } finally {
            ui.setLoading(false);
        }
    },

    renderDataGrid() {
        if (!this.meta) return;
        const fields = this.meta.fields;

        $('.btn-new-entity').off('click').on('click', () => {
            window.location.hash = `${this.currentDoctype}/Form`;
        });

        let headHtml = `<tr><th class="px-8 py-5 font-black tracking-widest text-xs text-gray-400 uppercase bg-gray-50/50 border-b border-gray-100 sticky left-0 z-10 bg-gray-50">Database ID</th>`;
        fields.forEach(f => {
            headHtml += `<th class="px-6 py-5 font-black tracking-widest text-xs text-gray-400 uppercase bg-gray-50/50 border-b border-gray-100 whitespace-nowrap">${f.label}</th>`;
        });
        headHtml += `<th class="px-8 py-5 text-right font-black tracking-widest text-xs text-gray-400 uppercase bg-gray-50/50 border-b border-gray-100 sticky right-0 z-10 bg-gray-50">Link</th></tr>`;
        $('#table-head').html(headHtml);

        if (this.data.length === 0) {
            $('#empty-state').removeClass('hidden');
            $('#table-body').html('');
            return;
        }

        let bodyHtml = '';
        this.data.forEach(row => {
            const rowId = row.id || 'N/A';
            bodyHtml += `
                <tr class="bg-white border-b border-gray-50 hover:bg-gray-50 transition-colors group cursor-pointer" onclick="window.location.hash='${this.currentDoctype}/Edit/${rowId}'">
                    <td class="px-8 py-6 font-mono text-xs text-primary-600 whitespace-nowrap sticky left-0 bg-white group-hover:bg-gray-50 transition-colors border-r border-gray-50">
                        <div class="flex items-center gap-2">
                            <div class="w-1.5 h-1.5 rounded-full bg-primary-400"></div>
                            ${rowId.toString().substring(0, 8).toUpperCase()}
                        </div>
                    </td>
                    ${fields.map(f => `<td class="px-6 py-6 font-bold text-gray-900 whitespace-nowrap">${this.formatValue(row[f.fieldname], f)}</td>`).join('')}
                    <td class="px-8 py-6 text-right sticky right-0 bg-white group-hover:bg-gray-50 transition-colors border-l border-gray-50">
                        <svg class="w-5 h-5 text-gray-300 group-hover:text-primary-600 ml-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                    </td>
                </tr>
            `;
        });
        $('#table-body').html(bodyHtml);
        $('#empty-state').addClass('hidden');
    },

    formatValue(val, f) {
        if (val === null || val === undefined || val === '') return '<span class="text-gray-300 font-light">--</span>';
        if (f.fieldtype === 'Link') return `<span class="bg-primary-50 text-primary-700 px-3 py-1 rounded-full text-[10px] uppercase font-black border border-primary-100">${val}</span>`;
        if (f.fieldtype === 'Currency') return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val);
        if (f.fieldtype === 'Check') return val ? `<span class="text-green-500 font-black">YES</span>` : `<span class="text-gray-200">NO</span>`;
        return val;
    },

    async renderFormPage(id = null) {
        ui.setLoading(true);
        try {
            const [meta, doc] = await Promise.all([
                api.getMeta(this.currentDoctype),
                id ? api.call('GET', `/api/get?table=${this.currentDoctype}&id=${id}`) : Promise.resolve({})
            ]);

            // "Add New" Context Restoration
            const pendingData = JSON.parse(localStorage.getItem('pending_form_data') || '{}');
            const returnCtx = JSON.parse(localStorage.getItem('return_context') || '{}');

            if (returnCtx.parentDoctype === this.currentDoctype) {
                Object.assign(doc, pendingData);
                const lastId = localStorage.getItem('last_created_id');
                if (lastId && returnCtx.fieldname) {
                    doc[returnCtx.fieldname] = lastId;
                    localStorage.removeItem('last_created_id');
                    localStorage.removeItem('return_context');
                    localStorage.removeItem('pending_form_data');
                }
            }

            this.meta = meta;
            let html = `
                <div class="max-w-6xl mx-auto">
                    <div class="flex items-center justify-between mb-10">
                        <div>
                            <button onclick="window.location.hash='${this.currentDoctype}'" class="text-primary-600 font-bold flex items-center gap-2 mb-2 hover:translate-x-[-4px] transition-transform">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>
                                Back to View
                            </button>
                            <h1 class="text-4xl font-black text-gray-900 tracking-tight">${id ? 'Update Entity' : 'New Strategic Record'}</h1>
                        </div>
                        <div class="flex gap-4">
                            <button onclick="engine.saveRecord()" class="px-10 py-4 bg-primary-600 text-white font-extrabold rounded-2xl shadow-xl shadow-primary-200 hover:scale-[1.02] active:scale-95 transition-all">Commit to SQL</button>
                        </div>
                    </div>
                    <div class="bg-white rounded-[2.5rem] border border-gray-100 shadow-2xl shadow-gray-200/50 p-12">
                        <form id="active-entity-form" class="grid grid-cols-2 gap-x-12 gap-y-10">
                            ${this.generateFormGroups(doc)}
                            <input type="hidden" name="doctype" value="${this.currentDoctype}">
                            ${id ? `<input type="hidden" name="id" value="${id}">` : ''}
                        </form>

                        <!-- Attachments Section -->
                        ${id ? `
                        <div class="mt-12 pt-10 border-t border-gray-100">
                            <h3 class="text-sm font-black text-primary-600 uppercase tracking-widest mb-6">Attachments</h3>
                            
                            <div class="grid grid-cols-2 gap-8">
                                <!-- Upload Box -->
                                <div class="border-2 border-dashed border-gray-300 rounded-2xl p-8 flex flex-col items-center justify-center text-center cursor-pointer hover:border-primary-400 hover:bg-primary-50/50 transition-colors" onclick="document.getElementById('file-upload').click()">
                                    <svg class="w-10 h-10 text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
                                    <p class="text-sm font-bold text-gray-600">Click to Upload File</p>
                                    <p class="text-xs text-gray-400 mt-1">PDF, PNG, JPG (Max 5MB)</p>
                                    <input type="file" id="file-upload" class="hidden" onchange="engine.handleFileUpload(this, '${this.currentDoctype}', '${id}')">
                                </div>
                                
                                <!-- File List -->
                                <div id="attachment-list" class="space-y-3">
                                    <p class="text-sm text-gray-400 italic">Loading files...</p>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Activity Log Section -->
                        <div class="mt-12 pt-10 border-t border-gray-100">
                            <h3 class="text-sm font-black text-orange-600 uppercase tracking-widest mb-6">
                                <svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                                Activity Log
                            </h3>
                            <div id="activity-log-container" class="space-y-3">
                                <p class="text-sm text-gray-400 italic">Loading activity...</p>
                            </div>
                        </div>
                        ` : ''}

                    </div>
                </div>
                
                <!-- Sticky Footer - Permission Aware -->
                <div class="fixed bottom-0 left-64 right-0 p-6 bg-white/80 backdrop-blur-xl border-t border-gray-200 flex justify-between items-center z-40">
                     <button onclick="engine.deleteRecord('${id}')" 
                             class="px-6 py-3 bg-red-50 text-red-600 font-bold rounded-xl hover:bg-red-100 transition-colors btn-delete-record ${!id || !(window.userPermissions?.canDelete) ? 'hidden' : ''}">
                        Delete Record
                    </button>
                    <div class="flex gap-4">
                        <button onclick="engine.printRecord('${id}')" class="px-6 py-3 bg-gray-100 text-gray-700 font-bold rounded-xl hover:bg-gray-200 transition-colors ${!id ? 'hidden' : ''}">
                            Print / PDF
                        </button>
                        <button onclick="window.history.back()" class="px-6 py-3 text-gray-500 font-bold hover:bg-gray-100 rounded-xl transition-colors">Cancel</button>
                        <button onclick="engine.saveRecord()" 
                                class="px-8 py-3 bg-gray-900 text-white font-bold rounded-xl shadow-lg shadow-gray-200 hover:bg-black hover:-translate-y-1 transition-transform btn-save-record ${!(window.userPermissions?.canUpdate || window.userPermissions?.canCreate) ? 'hidden' : ''}">
                            Save Changes
                        </button>
                    </div>
                </div>
            `;
            $('#app-viewport').html(html);
            if (id) {
                this.loadAttachments(this.currentDoctype, id);
                this.loadActivityLog(this.currentDoctype, id);
            }
        } catch (e) {
            ui.toast("Form Configuration Failed", "error");
        } finally {
            ui.setLoading(false);
        }
    },

    printRecord(id) {
        if (!id) return;

        const doctype = this.currentDoctype;
        const rawData = {};

        // 1. Harvest Data
        $('#active-entity-form').find('input, select, textarea').each(function () {
            const name = $(this).attr('name');
            if (!name || name === 'doctype' || name === 'id') return;

            let value = $(this).val();

            // Resolve Link Fields
            if ($(this).is('select')) {
                const text = $(this).find('option:selected').text();
                if (text && !text.startsWith('Link ')) value = text;
                else value = '';
            }
            rawData[name] = value;
        });
        rawData['id'] = id;
        rawData['date'] = new Date().toLocaleDateString();

        // 2. Select Template
        let contentHtml = '';
        let styles = '';

        if (doctype.includes('Invoice')) {
            // PROFESSIONAL INVOICE TEMPLATE
            styles = `
                .invoice-box { max-width: 800px; margin: auto; padding: 30px; border: 1px solid #eee; font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif; color: #555; }
                .invoice-header { display: flex; justify-content: space-between; margin-bottom: 50px; }
                .title { font-size: 45px; line-height: 45px; color: #333; font-weight: bold; text-transform: uppercase; }
                .meta-table td { padding: 5px; text-align: right; }
                .bill-to { margin-bottom: 40px; }
                .bill-to h3 { margin-top: 0; color: #333; }
                .total-box { background: #f8f8f8; border-top: 3px solid #333; padding: 20px; text-align: right; margin-top: 40px; }
                .total-label { font-size: 14px; font-weight: bold; text-transform: uppercase; color: #777; }
                .total-value { font-size: 30px; font-weight: bold; color: #000; }
                .line-item-header { font-weight: bold; background: #333; color: #fff; padding: 10px; display: flex; justify-content: space-between; }
                .line-item { border-bottom: 1px solid #eee; padding: 15px 10px; display: flex; justify-content: space-between; }
            `;

            contentHtml = `
                <div class="invoice-box">
                    <div class="invoice-header">
                        <div>
                            <div style="font-size: 20px; font-weight: bold; color: #333;">Consultancy OS</div>
                            <div>123 Business Park<br>Global City, 5000</div>
                        </div>
                        <div style="text-align: right;">
                            <div class="title">INVOICE</div>
                            <table class="meta-table" align="right">
                                <tr><td>Invoice #:</td><td><strong>${id.split('-')[0]}</strong></td></tr>
                                <tr><td>Date:</td><td>${rawData.date}</td></tr>
                                <tr><td>Due Date:</td><td>${rawData.DueDate || 'On Receipt'}</td></tr>
                            </table>
                        </div>
                    </div>

                    <div class="bill-to">
                        <h3>Bill To:</h3>
                        <div>${rawData.Client_Name || rawData.Consultants_name || 'Client / Consultant'}</div>
                        <div>${rawData.Email || ''}</div>
                        <div>${rawData.Phone || ''}</div>
                    </div>

                    <div class="line-items">
                        <div class="line-item-header">
                            <div>Description</div>
                            <div>Amount</div>
                        </div>
                        <div class="line-item">
                            <div>${rawData.Description || rawData.Title || 'Professional Services'}</div>
                            <div>$${rawData.TotalAmount || rawData.Amount || '0.00'}</div>
                        </div>
                    </div>

                    <div class="total-box">
                        <div class="total-label">Total Amount</div>
                        <div class="total-value">$${rawData.TotalAmount || rawData.Amount || '0.00'}</div>
                    </div>
                </div>
            `;

        } else if (doctype === 'Consultancy_Assignments') {
            // LEGAL CONTRACT TEMPLATE
            styles = `
                body { font-family: 'Times New Roman', serif; line-height: 1.6; color: #222; max-width: 800px; margin: 0 auto; padding: 40px; }
                h1 { text-align: center; text-decoration: underline; text-transform: uppercase; font-size: 24px; margin-bottom: 40px; }
                h2 { font-size: 16px; text-transform: uppercase; border-bottom: 1px solid #000; padding-bottom: 5px; margin-top: 30px; }
                p { margin-bottom: 15px; text-align: justify; }
                .contract-meta { margin-bottom: 30px; }
                .field-pair { display: flex; margin-bottom: 10px; }
                .label { font-weight: bold; width: 150px; }
                .signatures { margin-top: 80px; display: flex; justify-content: space-between; }
                .sig-block { width: 45%; border-top: 1px solid #000; padding-top: 10px; text-align: center; }
            `;

            contentHtml = `
                <h1>Consultancy Service Agreement</h1>
                
                <p>This Agreement is entered into on <strong>${rawData.date}</strong>, by and between:</p>
                
                <p><strong>CLIENT:</strong> ${rawData.Client_Name || '[Client Name]'}</p>
                <p>AND</p>
                <p><strong>CONSULTANT:</strong> ${rawData.LeadConsultant || rawData.Consultant || '[Consultant Name]'}</p>

                <h2>1. Scope of Services</h2>
                <div class="contract-meta">
                    <div class="field-pair"><div class="label">Project Title:</div><div>${rawData.Title}</div></div>
                    <div class="field-pair"><div class="label">Reference:</div><div>${rawData.ContractRef || id.split('-')[0]}</div></div>
                    <div class="field-pair"><div class="label">Start Date:</div><div>${rawData.StartDate || 'TBD'}</div></div>
                    <div class="field-pair"><div class="label">End Date:</div><div>${rawData.EndDate || 'TBD'}</div></div>
                </div>
                <p>The Consultant agrees to perform the services described in the "Scope of Work" attached hereto (or defined by the Role: ${rawData.Role || 'Advisor'}).</p>

                <h2>2. Compensation</h2>
                <p>The total value of this assignment is estimated at <strong>$${rawData.TotalValue || rawData.Amount || '0.00'}</strong>, payable according to the schedule defined in the project annexes.</p>

                <h2>3. Terms</h2>
                <p>This agreement is governed by the laws of the jurisdiction. Both parties execute this agreement by their authorized representatives.</p>

                <div class="signatures">
                    <div class="sig-block">
                        <strong>For the Client</strong><br>
                        Authorized Signature
                    </div>
                    <div class="sig-block">
                        <strong>For the Consultant</strong><br>
                        Authorized Signature
                    </div>
                </div>
            `;
        } else {
            // GENERIC FALLBACK (Clean Grid)
            styles = `
                    body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; padding: 60px; max-width: 900px; margin: 0 auto; color: #333; line-height: 1.6; }
                    .header { border-bottom: 3px solid #000; padding-bottom: 20px; margin-bottom: 40px; display: flex; justify-content: space-between; align-items: end; }
                    h1 { margin: 0; font-size: 28px; text-transform: uppercase; letter-spacing: 1px; }
                    .meta { font-size: 12px; color: #666; text-align: right; }
                    .field-row { display: flex; border-bottom: 1px solid #e0e0e0; padding: 12px 0; page-break-inside: avoid; }
                    .field-label { width: 35%; font-weight: 700; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: #888; padding-right: 20px; }
                    .field-value { width: 65%; font-size: 14px; font-weight: 500; color: #111; }
                    .footer { margin-top: 60px; font-size: 10px; text-align: center; color: #aaa; border-top: 1px solid #eee; padding-top: 20px; }
            `;

            const fieldsHtm = Object.entries(rawData).map(([k, v]) => {
                if (k === 'id' || k === 'date') return '';
                return `<div class="field-row"><div class="field-label">${k.replace(/_/g, ' ')}</div><div class="field-value">${v}</div></div>`;
            }).join('');

            contentHtml = `
                <div class="header"><h1>${doctype.replace(/_/g, ' ')}</h1><div class="meta">REF: ${id.split('-')[0]}<br>${rawData.date}</div></div>
                <div class="content">${fieldsHtm}</div>
                <div class="footer">CONFIDENTIAL | Generated by Consultancy OS</div>
            `;
        }

        // Write to Window
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`<html><head><title>${doctype} - ${id}</title><style>${styles} @media print { .no-print { display: none; } body { padding: 0; margin: 2cm; } }</style></head><body>${contentHtml}<script>window.onload = function() { window.print(); }</script></body></html>`);
        printWindow.document.close();
    },

    generateFormGroups(doc) {
        let html = '';
        this.meta.fields.forEach((f, idx) => {
            if (idx % 8 === 0) {
                html += `<div class="col-span-2 mt-10 mb-2 border-b border-gray-100 pb-2"><h3 class="text-sm font-black text-primary-600 uppercase tracking-[0.2em]">Section 0${Math.floor(idx / 8) + 1}</h3></div>`;
            }
            let val = doc[f.fieldname] || '';
            const col = f.fieldtype === 'Long Text' ? 'col-span-2' : 'col-span-1';

            if (f.fieldname === 'Status') {
                html += `<div class="${col} space-y-3"><label class="text-[10px] font-black text-gray-500 uppercase tracking-widest">${f.label}</label>
                <select name="Status" class="w-full p-5 bg-primary-50 border-none rounded-2xl font-bold text-primary-800 appearance-none">
                    <option value="Active" ${val === 'Active' ? 'selected' : ''}>Active</option>
                    <option value="Inactive" ${val === 'Inactive' ? 'selected' : ''}>Inactive</option>
                </select></div>`;
            } else if (f.fieldtype === 'Link') {
                html += `<div class="${col} space-y-3"><label class="text-[10px] font-black text-gray-500 uppercase tracking-widest">${f.label}</label>
                <select name="${f.fieldname}" onchange="engine.handleSelectChange('${this.currentDoctype}', '${f.fieldname}', '${f.options}', this.value)" class="w-full p-5 bg-gray-50 border-none rounded-2xl font-bold text-gray-900 appearance-none">
                    <option value="">Link ${f.options}...</option>
                    <option value="ADD_NEW" class="text-primary-600 font-black">+ Add New ${f.options}...</option>
                </select><div id="preview-${f.fieldname}"></div></div>`;
                api.getList(f.options).then(opts => {
                    const sel = $(`select[name="${f.fieldname}"]`);
                    opts.forEach(o => {
                        // Advanced Enterprise Naming Heuristic
                        const label = o.Role_EN || o.country_name || o.Governorates || o.ServiceLines || o.ContactName || o.Title || o.Client_Name || o.Consultants_name || o.Item_Name || o.name || o.label || o.id;
                        sel.append(`<option value="${o.id}" ${val == o.id ? 'selected' : ''}>${label.toString().toUpperCase()}</option>`);
                    });
                });
            } else {
                const isReadOnly = f.read_only ? 'readonly tabindex="-1"' : '';
                const styleClasses = f.read_only ? 'bg-gray-200/50 text-gray-500 cursor-not-allowed border-transparent focus:ring-0' : 'bg-gray-50 text-gray-900 border-none';

                html += `<div class="${col} space-y-3"><label class="text-[10px] font-black text-gray-500 uppercase tracking-widest">${f.label} ${f.read_only ? '(LOCKED)' : ''}</label>
                <input type="text" name="${f.fieldname}" value="${val}" ${isReadOnly} class="w-full p-5 rounded-2xl font-bold ${styleClasses}"></div>`;
            }
        });
        return html;
    },

    async handleSelectChange(pDt, fn, tDt, val) {
        if (val === 'ADD_NEW') {
            const data = {};
            new FormData(document.querySelector('#active-entity-form')).forEach((v, k) => data[k] = v);
            localStorage.setItem('pending_form_data', JSON.stringify(data));
            localStorage.setItem('return_context', JSON.stringify({ parentDoctype: pDt, fieldname: fn, id: data.id }));
            window.location.hash = `${tDt}/Form`;
            return;
        }
        this.fetchRelationalPreview(tDt, val, fn);
    },


    async fetchRelationalPreview(table, id, fieldname) {
        const container = $(`#preview-${fieldname}`);
        if (!id) return container.html('');
        const preview = await api.getPreview(table, id);
        let items = '';
        for (let [k, v] of Object.entries(preview)) if (k !== 'id') items += `<div><p class="text-[8px] uppercase text-gray-400">${k}</p><p class="text-xs font-bold text-primary-700">${v}</p></div>`;
        container.html(`<div class="p-4 bg-primary-50 rounded-xl grid grid-cols-2 gap-2 mt-2 border border-primary-100">${items}</div>`);
    },


    async renderDashboard() {
        ui.setLoading(true);
        try {
            // Load Template
            const template = await fetch('/portal/pages/dashboard.html').then(r => r.text());
            $('#app-viewport').html(template);

            // Update Date
            $('#date-display').text(new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }));

            // Fetch Data in Parallel
            const [assignments, consultants, services, tasks, stages] = await Promise.all([
                api.getList('Consultancy_Assignments'),
                api.getList('Consultants'),
                api.getList('ServiceLines'),
                api.getList('Tasks'),
                api.getList('Stages')
            ]);

            // 1. Calculate Quick Stats
            $('#stat-active-projects').text(assignments.filter(a => a.Status === 'Active').length);
            $('#stat-total-consultants').text(consultants.length);
            $('#stat-total-services').text(services.length);

            // 2. Render Charts
            this.renderCharts(assignments, consultants, stages);

            // 3. Render Tasks Feed
            this.renderRecentTasks(tasks);

            // 4. Permission Check: Toggle Action Cards vs Charts
            if (window.userPermissions && !window.userPermissions.canCreate) {
                $('#dashboard-action-cards').addClass('hidden');
                $('#dashboard-read-only-charts').removeClass('hidden');
                this.renderReadOnlyCharts(tasks, assignments, consultants);
            }

        } catch (e) {
            console.error(e);
            ui.toast("Dashboard Partial Load Error", "error");
        } finally {
            ui.setLoading(false);
        }
    },

    renderReadOnlyCharts(tasks, assignments, consultants) {
        // Chart 1: Task Efficiency (Completed vs Pending)
        const completed = tasks.filter(t => t.Status === 'Completed').length;
        const pending = tasks.length - completed;
        new Chart(document.getElementById('chart-ro-tasks'), {
            type: 'doughnut',
            data: { labels: ['Done', 'Pending'], datasets: [{ data: [completed, pending], backgroundColor: ['#f97316', '#fed7aa'], borderWidth: 0 }] },
            options: { cutout: '70%', plugins: { legend: { display: false } }, responsive: true, maintainAspectRatio: false }
        });

        // Chart 2: Project Types (Simple Distribution)
        const types = {};
        assignments.forEach(a => types[a.ProjectType || 'General'] = (types[a.ProjectType || 'General'] || 0) + 1);
        new Chart(document.getElementById('chart-ro-projects'), {
            type: 'pie',
            data: { labels: Object.keys(types), datasets: [{ data: Object.values(types), backgroundColor: ['#3b82f6', '#93c5fd', '#1e40af'], borderWidth: 0 }] },
            options: { plugins: { legend: { display: false } }, responsive: true, maintainAspectRatio: false }
        });

        // Chart 3: Utilization (Active vs Inactive Consultants)
        const active = consultants.filter(c => c.Status === 'Active').length;
        const inactive = consultants.length - active;
        new Chart(document.getElementById('chart-ro-utilization'), {
            type: 'doughnut',
            data: { labels: ['Active', 'Bench'], datasets: [{ data: [active, inactive], backgroundColor: ['#a855f7', '#e9d5ff'], borderWidth: 0 }] },
            options: { cutout: '70%', plugins: { legend: { display: false } }, responsive: true, maintainAspectRatio: false }
        });
    },

    async renderSettingsPage() {
        ui.setLoading(true);
        try {
            const template = await fetch('/portal/pages/settings.html').then(r => r.text());
            $('#app-viewport').html(template);

            // Initialize the settings page - load general settings by default
            if (window.loadGeneralSettings) {
                await window.loadGeneralSettings();
            }
        } catch (e) {
            console.error("Settings page load error:", e);
            ui.toast("Failed to load Settings page", "error");
        } finally {
            ui.setLoading(false);
        }
    },

    renderCharts(assignments, consultants, stages) {
        // Prepare Data: Project Stages
        const stageCounts = {};
        stages.forEach(s => stageCounts[s.Stages] = 0); // Init
        assignments.forEach(a => {
            // Look up stage name if possible (assuming 'Stage' field in assignment is ID or Name. The schema says Stage is Linked to Stages).
            // Since we only have IDs in the Assignment list usually (unless expanded), we might need to map IDs.
            // But getList returns raw table data. 'Stage' col in Assignments likely holds the ID of the Stage.
            // We need to map StageID -> StageName.
            const stageNameObj = stages.find(s => s.id === a.Stage);
            const stageName = stageNameObj ? stageNameObj.Stages : 'Unknown';
            stageCounts[stageName] = (stageCounts[stageName] || 0) + 1;
        });

        const ctxStages = document.getElementById('chart-stages').getContext('2d');
        new Chart(ctxStages, {
            type: 'bar',
            data: {
                labels: Object.keys(stageCounts),
                datasets: [{
                    label: 'Projects',
                    data: Object.values(stageCounts),
                    backgroundColor: '#3b82f6',
                    borderRadius: 8,
                    barThickness: 40
                }]
            },
            options: {
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, grid: { borderDash: [2, 4], color: '#f3f4f6' } },
                    x: { grid: { display: false } }
                }
            }
        });

        // Prepare Data: Consultant Distribution (Simplistic for now - random or status)
        const activeCons = consultants.filter(c => c.Status === 'Active').length;
        const inactiveCons = consultants.length - activeCons;

        const ctxCons = document.getElementById('chart-consultants').getContext('2d');
        new Chart(ctxCons, {
            type: 'doughnut',
            data: {
                labels: ['Active', 'Inactive'],
                datasets: [{
                    data: [activeCons, inactiveCons],
                    backgroundColor: ['#10b981', '#cbd5e1'],
                    borderWidth: 0
                }]
            },
            options: {
                cutout: '75%',
                plugins: { legend: { display: false } }
            }
        });
    },

    renderRecentTasks(tasks) {
        const recent = tasks.slice(0, 5);
        if (recent.length === 0) {
            $('#dashboard-tasks-table').html('<tr><td colspan="4" class="text-center py-4 text-gray-400">No active tasks found.</td></tr>');
            return;
        }

        const html = recent.map(t => `
            <tr class="border-b border-gray-50 last:border-none hover:bg-gray-50 transition-colors">
                <td class="pl-4 py-4 font-bold text-gray-800 text-sm">${t.Title}</td>
                <td class="py-4 text-xs text-gray-500 font-mono">${t.Consultant ? 'Linked' : '--'}</td>
                <td class="py-4 text-xs font-bold text-gray-400">${t.DueDate || 'No Date'}</td>
                <td class="pr-4 py-4 text-right">
                    <span class="px-2 py-1 rounded-full text-[10px] font-black uppercase ${t.Status === 'Completed' ? 'bg-green-100 text-green-600' : 'bg-orange-100 text-orange-600'}">
                        ${t.Status || 'Pending'}
                    </span>
                </td>
            </tr>
        `).join('');
        $('#dashboard-tasks-table').html(html);
    },


    /* -------------------------------------------------------------------------- */
    /*                         SPECIFIC MODULE RENDERERS                          */
    /* -------------------------------------------------------------------------- */

    async renderClientsDashboard(data) {
        // 1. Stats
        $('#stat-total-clients').text(data.length);

        // 2. Chart: Client Types
        const types = {};
        data.forEach(c => types[c.ClientType] = (types[c.ClientType] || 0) + 1);

        // Render Chart
        const ctx = document.getElementById('chart-client-types').getContext('2d');
        const colors = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444'];
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(types),
                datasets: [{ data: Object.values(types), backgroundColor: colors, borderWidth: 0 }]
            },
            options: { plugins: { legend: { display: false } }, cutout: '70%' }
        });

        // Legend
        const legendHtml = Object.keys(types).map((t, i) =>
            `<div class="flex items-center gap-2"><div class="w-2 h-2 rounded-full" style="background:${colors[i % colors.length]}"></div><span class="text-xs font-bold text-gray-500">${t}</span></div>`
        ).join('');
        $('#client-legend').html(legendHtml);
    },

    async renderConsultantsDashboard(data) {
        // 1. Stats
        const active = data.filter(c => c.Status === 'Active').length;
        $('#stat-total-cons').text(data.length);
        $('#stat-active-cons').text(active);
        $('#stat-bench-cons').text(data.length - active);

        // 2. Chart
        const ctx = document.getElementById('chart-consultant-status').getContext('2d');
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['Active', 'Inactive'],
                datasets: [{ data: [active, data.length - active], backgroundColor: ['#22c55e', '#f97316'], borderWidth: 0 }]
            },
            options: { plugins: { legend: { display: false } } }
        });
    },

    async renderAssignmentsDashboard(data) {
        // 1. Stats
        const active = data.filter(a => a.Status === 'Active').length;
        const total = data.length;
        const inactive = total - active;
        const pctActive = total ? Math.round((active / total) * 100) : 0;

        $('#stat-inactive').text(inactive);
        $('#prog-active-val').text(pctActive + '%');
        $('#prog-active-bar').css('width', pctActive + '%');

        // 2. Chart: Priority
        const priority = {};
        data.forEach(a => priority[a.Priority] = (priority[a.Priority] || 0) + 1);

        const ctx = document.getElementById('chart-priority').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(priority),
                datasets: [{
                    label: 'Count',
                    data: Object.values(priority),
                    backgroundColor: 'rgba(255, 255, 255, 0.2)',
                    borderColor: 'rgba(255, 255, 255, 1)',
                    borderWidth: 1,
                    borderRadius: 4,
                    barThickness: 20
                }]
            },
            options: {
                indexAxis: 'y',
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false, drawBorder: false }, ticks: { display: false } },
                    y: { grid: { display: false, drawBorder: false }, ticks: { color: 'white', font: { weight: 'bold' } } }
                }
            }
        });
    },

    async renderTasksDashboard(data) {
        const completed = data.filter(t => t.Status === 'Completed').length;
        const pending = data.length - completed;

        $('#val-pending-tasks').text(pending);
        $('#val-completed-tasks').text(completed);

        const ctx = document.getElementById('chart-task-completion').getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Done', 'Pending'],
                datasets: [{ data: [completed, pending], backgroundColor: ['#22c55e', '#e5e7eb'], borderWidth: 0 }]
            },
            options: { cutout: '60%', plugins: { legend: { display: false } } }
        });
    },

    renderCardGrid() {
        const data = this.data;
        let html = '';

        if (this.currentDoctype === 'Clients') {
            data.forEach(d => {
                const init = d.Client_Name ? d.Client_Name.substring(0, 2).toUpperCase() : 'CO';
                html += `
                <div class="bg-white p-6 rounded-[2rem] border border-gray-100 shadow-lg shadow-gray-100/50 hover:-translate-y-1 transition-transform cursor-pointer group relative overflow-hidden" onclick="window.location.hash='Clients/Edit/${d.id}'">
                    <div class="absolute top-0 right-0 w-16 h-16 bg-gradient-to-br from-primary-400 to-primary-600 rounded-bl-[2rem] flex items-center justify-center text-white font-black text-xs shadow-lg shadow-primary-200">${d.ClientCode || 'N/A'}</div>
                    <div class="w-12 h-12 bg-gray-50 rounded-xl mb-4 flex items-center justify-center text-xl font-black text-gray-400 group-hover:bg-primary-50 group-hover:text-primary-600 transition-colors">${init}</div>
                    <h3 class="font-bold text-gray-900 text-lg leading-tight mb-1 line-clamp-1">${d.Client_Name}</h3>
                    <p class="text-xs text-gray-400 font-bold uppercase tracking-widest mb-4">${d.ClientType || 'Unknown'}</p>
                    <div class="flex gap-2">
                        <span class="px-3 py-1 bg-green-50 text-green-600 rounded-lg text-xs font-bold border border-green-100">${d.Status || 'Active'}</span>
                    </div>
                </div>`;
            });
        }
        else if (this.currentDoctype === 'Consultants') {
            data.forEach(d => {
                html += `
                <div class="bg-white p-6 rounded-[2rem] border border-gray-100 shadow-lg shadow-gray-100/50 hover:-translate-y-1 transition-transform cursor-pointer group" onclick="window.location.hash='Consultants/Edit/${d.id}'">
                    <div class="flex items-center gap-4 mb-4">
                        <div class="w-12 h-12 rounded-full bg-indigo-50 flex items-center justify-center text-indigo-600 font-black text-lg border border-indigo-100 shadow-sm">${d.Consultants_name ? d.Consultants_name.substring(0, 1) : 'U'}</div>
                        <div>
                            <h3 class="font-bold text-gray-900 leading-tight">${d.Consultants_name}</h3>
                            <p class="text-xs text-gray-400">${d.JobTitle || 'Consultant'}</p>
                        </div>
                    </div>
                    <div class="space-y-2">
                        <div class="flex justify-between items-center p-3 bg-gray-50 rounded-xl">
                             <span class="text-[10px] font-bold text-gray-400 uppercase">Rating</span>
                             <span class="text-xs font-black text-gray-900">★★★★☆</span>
                        </div>
                        <div class="flex justify-between items-center p-3 bg-gray-50 rounded-xl">
                             <span class="text-[10px] font-bold text-gray-400 uppercase">Status</span>
                             <span class="text-xs font-black ${d.Status === 'Active' ? 'text-green-500' : 'text-orange-500'}">${d.Status || 'Active'}</span>
                        </div>
                    </div>
                </div>`;
            });
        }

        $('#card-grid').html(html);
        if (data.length === 0) $('#card-grid').html('<div class="col-span-4 text-center text-gray-300 font-bold italic py-10">No records found</div>');
    },

    async deleteRecord(id) {
        if (!confirm("Are you sure you want to PERMANENTLY delete this record? This action cannot be undone.")) return;

        ui.setLoading(true);
        try {
            await api.post('/api/delete', {
                doctype: this.currentDoctype,
                id: id
            });
            ui.toast("Record Deleted", "success");
            window.location.hash = this.currentDoctype;
        } catch (e) {
            ui.toast("Delete Failed: " + e.message, "error");
        } finally {
            ui.setLoading(false);
        }
    },

    exportToCSV() {
        if (!this.data || !this.data.length) {
            ui.toast("No data to export", "error");
            return;
        }

        const data = this.data;
        const headers = Object.keys(data[0]);
        const csvRows = [];

        // Header Row
        csvRows.push(headers.join(','));

        // Data Rows
        for (const row of data) {
            const values = headers.map(header => {
                const escaped = ('' + (row[header] || '')).replace(/"/g, '\\"');
                return `"${escaped}"`;
            });
            csvRows.push(values.join(','));
        }

        const csvString = csvRows.join('\n');
        const blob = new Blob([csvString], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.setAttribute('hidden', '');
        a.setAttribute('href', url);
        a.setAttribute('download', `${this.currentDoctype}_export_${new Date().toISOString().slice(0, 10)}.csv`);
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    },

    async handleFileUpload(input, doctype, id) {
        const file = input.files[0];
        if (!file) return;

        // Base64 Conversion
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = async () => {
            ui.setLoading(true);
            try {
                await api.post('/api/upload', {
                    filename: file.name,
                    content: reader.result,
                    parent_doctype: doctype,
                    parent_id: id
                });
                ui.toast("File Uploaded", "success");
                this.loadAttachments(doctype, id); // Refresh list
            } catch (e) {
                ui.toast("Upload Failed: " + e.message, "error");
            } finally {
                ui.setLoading(false);
            }
        };
    },

    async loadAttachments(doctype, id) {
        try {
            const files = await api.call('GET', `/api/files?doctype=${doctype}&id=${id}`);
            const html = files.map(f => `
                <div class="flex items-center justify-between p-4 bg-gray-50 rounded-xl border border-gray-100 hover:border-primary-200 transition-colors">
                    <div class="flex items-center gap-3 overflow-hidden">
                        <div class="w-10 h-10 bg-white rounded-lg flex items-center justify-center text-primary-600 shadow-sm font-bold text-xs uppercase border border-gray-100">
                            ${f.file_name.split('.').pop()}
                        </div>
                        <div class="truncate">
                            <a href="${f.file_path}" target="_blank" class="text-sm font-bold text-gray-900 hover:text-primary-600 block truncate">${f.file_name}</a>
                            <p class="text-[10px] text-gray-400 font-mono">${f.uploaded_at}</p>
                        </div>
                    </div>
                    <a href="${f.file_path}" download class="text-gray-400 hover:text-primary-600">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                    </a>
                </div>
            `).join('');
            $('#attachment-list').html(html || '<p class="text-sm text-gray-300 italic p-4">No attachments yet.</p>');
        } catch (e) {
            console.error(e);
        }
    },

    async loadActivityLog(doctype, id) {
        try {
            const logs = await api.call('GET', `/api/audit?doctype=${doctype}&id=${id}&limit=20`);

            if (!logs || logs.length === 0) {
                $('#activity-log-container').html('<p class="text-sm text-gray-300 italic p-4">No activity recorded yet.</p>');
                return;
            }

            const html = logs.map(log => {
                // Format timestamp
                const date = new Date(log.timestamp);
                const timeAgo = this.formatTimeAgo(date);

                // Action badge color
                let badgeClass = 'bg-blue-100 text-blue-700';
                if (log.action === 'CREATE') badgeClass = 'bg-green-100 text-green-700';
                if (log.action === 'DELETE') badgeClass = 'bg-red-100 text-red-700';
                if (log.action === 'UPDATE') badgeClass = 'bg-orange-100 text-orange-700';

                // Parse changes
                let changesHtml = '';
                if (log.changes && log.action === 'UPDATE') {
                    try {
                        const changes = JSON.parse(log.changes);
                        const changeItems = Object.entries(changes).map(([field, vals]) =>
                            `<span class="text-[10px] bg-gray-100 px-2 py-1 rounded">${field}: ${vals.old || '(empty)'} → ${vals.new || '(empty)'}</span>`
                        ).join(' ');
                        changesHtml = `<div class="mt-2 flex flex-wrap gap-1">${changeItems}</div>`;
                    } catch (e) { }
                }

                return `
                    <div class="flex items-start gap-4 p-4 bg-gray-50 rounded-xl border border-gray-100 hover:shadow-sm transition-all">
                        <div class="w-8 h-8 rounded-full bg-white border border-gray-200 flex items-center justify-center text-xs font-bold text-gray-500 shrink-0">
                            ${(log.username || 'S')[0].toUpperCase()}
                        </div>
                        <div class="flex-1 min-w-0">
                            <div class="flex items-center gap-2 flex-wrap">
                                <span class="font-bold text-gray-900 text-sm">${log.username || 'System'}</span>
                                <span class="px-2 py-0.5 rounded text-[10px] font-black uppercase ${badgeClass}">${log.action}</span>
                                <span class="text-xs text-gray-400">${timeAgo}</span>
                            </div>
                            <p class="text-sm text-gray-600 mt-1">${log.summary || ''}</p>
                            ${changesHtml}
                        </div>
                    </div>
                `;
            }).join('');

            $('#activity-log-container').html(html);
        } catch (e) {
            console.error('Activity Log Error:', e);
            $('#activity-log-container').html('<p class="text-sm text-red-400 italic p-4">Failed to load activity.</p>');
        }
    },

    formatTimeAgo(date) {
        const seconds = Math.floor((new Date() - date) / 1000);
        if (seconds < 60) return 'just now';
        if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
        if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
        if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
        return date.toLocaleDateString();
    },

    async saveRecord() {
        const form = document.querySelector('#active-entity-form');
        const data = {};
        new FormData(form).forEach((v, k) => data[k] = v);
        ui.setLoading(true);
        try {
            const res = await api.save(data);
            ui.toast("Record Committed", "success");
            const ctx = JSON.parse(localStorage.getItem('return_context') || '{}');
            if (ctx.parentDoctype) {
                localStorage.setItem('last_created_id', res.id);
                window.location.hash = ctx.id ? `${ctx.parentDoctype}/Edit/${ctx.id}` : `${ctx.parentDoctype}/Form`;
            } else {
                window.location.hash = this.currentDoctype;
            }
        } catch (e) {
            ui.toast("Error: " + e.message, "error");
        } finally {
            ui.setLoading(false);
        }
    }
};

window.engine = engine; // Global Export

// --- SETTINGS MODULE ---

window.loadGeneralSettings = async function () {
    try {
        const settings = await api.call('GET', '/api/settings/get');
        if (settings.system_name) $('#setting-system-name').val(settings.system_name);
        if (settings.system_logo) $('#setting-system-logo').val(settings.system_logo);
        // Map theme to UI state if needed
    } catch (e) { console.error(e); }
};

window.saveGeneralSettings = async function () {
    const data = {
        'system_name': $('#setting-system-name').val(),
        'system_logo': $('#setting-system-logo').val()
    };
    ui.setLoading(true);
    try {
        await api.post('/api/settings/save', data);
        ui.toast("Configuration Saved", "success");

        // Apply immediately to the UI (Real Authority)
        if (window.applySystemSettings) await window.applySystemSettings();

    } catch (e) {
        ui.toast("Save Failed", "error");
    } finally {
        ui.setLoading(false);
    }
};

window.setTheme = async function (theme) {
    ui.setLoading(true);
    try {
        const data = { 'theme': theme };
        await api.post('/api/settings/save', data);

        // Apply class immediately for instant feedback
        if (window.applyThemeClasses) window.applyThemeClasses(theme);

        ui.toast(`Environment theme updated to ${theme.toUpperCase()}`, "info");
    } catch (e) {
        ui.toast("Theme update failed", "error");
    } finally {
        ui.setLoading(false);
    }
};

// --- USER MANAGEMENT ---

window.loadUsers = async function () {
    try {
        const users = await api.call('GET', '/api/users/list');
        $('#user-count').text(users.length);
        const html = users.map(u => `
            <tr class="border-b border-gray-50 hover:bg-gray-50">
                <td class="px-8 py-4">
                    <div class="font-bold text-gray-900">${u.full_name}</div>
                    <div class="text-xs text-gray-400 font-mono">@${u.username}</div>
                </td>
                <td class="px-8 py-4"><span class="bg-blue-50 text-blue-600 px-3 py-1 rounded-lg text-xs font-bold uppercase">${u.role}</span></td>
                <td class="px-8 py-4 text-sm text-gray-600">${u.email || '-'}</td>
                <td class="px-8 py-4 text-right">
                    <button onclick="editUser('${u.id}', '${u.username}', '${u.full_name}', '${u.role}', '${u.email}')" class="text-gray-400 hover:text-primary-600 font-bold text-xs uppercase mr-4">Edit</button>
                    ${u.username !== 'admin' ? `<button onclick="deleteUser('${u.id}')" class="text-red-300 hover:text-red-500 font-bold text-xs uppercase">Delete</button>` : ''}
                </td>
            </tr>
        `).join('');
        $('#users-table-body').html(html);
    } catch (e) {
        ui.toast("Failed to load users", "error");
    }
};

window.openUserModal = function () {
    $('#modal-title').text("Add New User");
    $('#modal-user-id').val('');
    $('#modal-username').val('');
    $('#modal-fullname').val('');
    $('#modal-email').val('');
    $('#modal-password').val('');
    $('#user-modal').removeClass('hidden');
};

window.editUser = function (id, username, fullname, role, email) {
    $('#modal-title').text("Edit User");
    $('#modal-user-id').val(id);
    $('#modal-username').val(username);
    $('#modal-fullname').val(fullname);
    $('#modal-role').val(role);
    $('#modal-email').val(email);
    $('#modal-password').val(''); // Blank means no change
    $('#user-modal').removeClass('hidden');
};

window.closeUserModal = function () {
    $('#user-modal').addClass('hidden');
};

window.saveUser = async function () {
    const data = {
        id: $('#modal-user-id').val(),
        username: $('#modal-username').val(),
        full_name: $('#modal-fullname').val(),
        role: $('#modal-role').val(),
        email: $('#modal-email').val(),
        password: $('#modal-password').val()
    };

    if (!data.username || !data.full_name) return ui.toast("Name and Username required", "error");

    ui.setLoading(true);
    try {
        await api.post('/api/users/save', data);
        ui.toast("User Saved", "success");
        closeUserModal();
        loadUsers();
    } catch (e) {
        ui.toast(e.message, "error");
    } finally {
        ui.setLoading(false);
    }
};

window.deleteUser = async function (id) {
    if (!confirm("Delete this user?")) return;
    try {
        await api.post('/api/users/delete', { id });
        loadUsers();
        ui.toast("User Deleted", "success");
    } catch (e) {
        ui.toast("Delete failed", "error");
    }
};
