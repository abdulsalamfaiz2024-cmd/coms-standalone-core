
/**
 * CONSULTANCY OS - UI SYSTEM LAYER
 * Manages User Experience and Visual Feedback
 */
const ui = {
    toast(msg, type = 'info') {
        const color = type === 'error' ? 'red' : (type === 'success' ? 'green' : 'blue');
        const icon = type === 'error' ? 'M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z' : 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z';
        const id = 'toast-' + Math.random().toString(36).substr(2, 9);
        const html = `
            <div id="${id}" class="flex items-center w-full max-w-xs p-4 text-gray-500 bg-white rounded-2xl shadow-xl border border-gray-100 animate-in fade-in slide-in-from-right-10" role="alert">
                <div class="inline-flex items-center justify-center flex-shrink-0 w-8 h-8 text-${color}-500 bg-${color}-100 rounded-lg">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="${icon}"></path></svg>
                </div>
                <div class="ml-3 text-sm font-bold text-gray-900">${msg}</div>
            </div>
        `;
        $('#toast-container').append(html);
        setTimeout(() => $(`#${id}`).fadeOut(() => $(`#${id}`).remove()), 4000);
    },
    setLoading(isLoading) {
        if (isLoading) {
            $('#app-viewport').css('opacity', '0.5').css('pointer-events', 'none');
        } else {
            $('#app-viewport').css('opacity', '1').css('pointer-events', 'auto');
        }
    }
};
window.ui = ui; // Global Export
