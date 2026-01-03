/**
 * CONSULTANCY OS - BOOTSTRAPPER
 * Initializes the modular architecture and applies system settings & permissions
 */
$(document).ready(async () => {
    // 1. Auth Guard
    const token = localStorage.getItem('auth_token');
    const path = window.location.pathname;

    // If no token and not on login page, redirect
    if (!token && !path.includes('login.html')) {
        window.location.href = '/portal/login.html';
        return;
    }

    // 2. Load System Settings (Real Authority)
    window.applySystemSettings = async function () {
        try {
            const settings = await api.call('GET', '/api/settings/get');

            // Apply System Name
            if (settings.system_name) {
                document.title = `${settings.system_name} | Enterprise Engine`;
                $('#sidebar-system-name').text(settings.system_name);
            }

            // Apply Logo
            if (settings.system_logo) {
                if (settings.system_logo.startsWith('http') || settings.system_logo.startsWith('data:') || settings.system_logo.startsWith('/')) {
                    $('#sidebar-logo-image').attr('src', settings.system_logo).removeClass('hidden');
                    $('#sidebar-logo-letter').addClass('hidden');
                }
            }

            // Apply Theme
            if (settings.theme) {
                applyThemeClasses(settings.theme);
            }
        } catch (e) {
            console.error("Failed to load system settings", e);
        }
    };

    window.applyThemeClasses = function (theme) {
        $('html').removeClass('dark light theme-blue');
        if (theme === 'dark') $('html').addClass('dark');
        else if (theme === 'light') $('html').addClass('light');
        else if (theme === 'blue') $('html').addClass('theme-blue');

        // Save to local for persistence during transitions if needed
        localStorage.setItem('system_theme', theme);
    }

    // 3. Apply Role-Based Permissions
    window.applyPermissions = function () {
        const userInfo = JSON.parse(localStorage.getItem('user_info') || '{}');
        const permissions = userInfo.permissions || {};
        const role = userInfo.role || 'Viewer';

        console.log(`Applying permissions for role: ${role}`);

        // Get allowed modules
        const allowedModules = permissions.modules || [];
        const restrictedModules = permissions.restricted_modules || [];
        const allowedActions = permissions.actions || ['read'];

        // Store permissions globally for access elsewhere
        window.userPermissions = {
            role: role,
            modules: allowedModules,
            restrictedModules: restrictedModules,
            actions: allowedActions,
            canCreate: allowedActions.includes('create'),
            canUpdate: allowedActions.includes('update'),
            canDelete: allowedActions.includes('delete'),
            canManageUsers: permissions.can_manage_users || false,
            canViewFinancials: permissions.can_view_financials || false,
            canViewSettings: permissions.can_view_settings || false,
            isAdmin: allowedModules.includes('*')
        };

        // Hide sidebar items based on permissions
        $('#sidebar ul li a').each(function () {
            const href = $(this).attr('href');
            if (!href) return;

            const module = href.replace('#', '').split('/')[0];

            // Skip special items
            if (['Dashboard'].includes(module)) return;

            // Check if module is accessible
            const isAllowed = window.userPermissions.isAdmin ||
                allowedModules.includes(module) ||
                !restrictedModules.includes(module);

            if (!isAllowed) {
                $(this).closest('li').addClass('hidden permission-hidden');
            }
        });

        // Hide Settings link for non-admins
        if (!window.userPermissions.canViewSettings) {
            $('a[href="#Settings"]').closest('li').addClass('hidden');
        }

        // Hide financial modules for users without financial access
        if (!window.userPermissions.canViewFinancials) {
            ['Client_Invoices', 'Consultant_Invoices', 'Expenses'].forEach(m => {
                $(`a[href="#${m}"]`).closest('li').addClass('hidden permission-hidden-financial');
            });
        }

        // Update UI to reflect permission level
        if (!window.userPermissions.canCreate) {
            $('.btn-new-entity').addClass('hidden');
        }

        console.log('Permissions applied:', window.userPermissions);
    };

    if (token) {
        // Load User Info
        const userInfo = JSON.parse(localStorage.getItem('user_info') || '{}');
        $('#user-name-display').text(userInfo.name || 'User');
        $('#user-role-display').text(userInfo.role || 'Member');

        // Apply settings
        await applySystemSettings();

        // Apply permissions
        applyPermissions();
    }

    // 4. Initial Navigation
    if (typeof engine !== 'undefined') {
        engine.navigate();
    }

    // 5. Hash Change Listener - also check permissions on navigation
    window.onhashchange = () => {
        if (typeof engine !== 'undefined') {
            // Check if user can access the target module
            const hash = window.location.hash.replace('#', '');
            const module = hash.split('/')[0];

            if (window.userPermissions && !window.userPermissions.isAdmin) {
                if (window.userPermissions.restrictedModules.includes(module)) {
                    ui.toast('Access Denied: You do not have permission to access this module', 'error');
                    window.location.hash = 'Dashboard';
                    return;
                }
            }

            engine.navigate();
        }
    };

    console.log("Modular Enterprise Stack Initialized with Settings & Permissions Authority");
});
