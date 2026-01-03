/**
 * CONSULTANCY OS - API SERVICE LAYER
 * Secure communication with SQL Backend
 */
const api = {
    async call(method, path, data = null) {
        const options = {
            method,
            headers: { 'Content-Type': 'application/json' }
        };
        if (data) options.body = JSON.stringify(data);
        const res = await fetch(path, options);
        if (!res.ok) throw new Error(await res.text());
        return res.json();
    },
    getMeta: (dt) => api.call('GET', `/api/meta?doctype=${dt}`),
    getList: (table, search) => api.call('GET', `/api/list?table=${table}${search ? `&search=${search}` : ''}`),
    getPreview: (table, id) => api.call('GET', `/api/preview?table=${table}&id=${id}`),
    save: (data) => api.call('POST', '/api/save', data),
    post: (path, data) => api.call('POST', path, data)
};
window.api = api; // Global Export
