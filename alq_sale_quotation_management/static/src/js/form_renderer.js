odoo.define('alq.web.FormRenderer', function (require) {
    "use strict";

    var FormRenderer = require('web.FormRenderer');
    var config = require('web.config');
    var core = require('web.core');
    var dom = require('web.dom');

    var _t = core._t;
    var qweb = core.qweb;

    FormRenderer.include({

        getLocalState: function () {
            const state = {};
            for (const notebook of this.el.querySelectorAll(':scope div.o_notebook')) {
                const name = notebook.dataset.name;
                const navs = notebook.querySelectorAll(':scope .o_notebook_headers .nav-item > .nav-link');
                state[name] = Math.max([...navs].findIndex(
                    nav => nav.classList.contains('active')
                ), 0);
            }
            state.scrollTop = $('.o_content').scrollTop();
            //  state.scrollValue = $('.o_content').scrollTop();
            return state;
        },

        setLocalState: function (state) {
            for (const notebook of this.el.querySelectorAll(':scope div.o_notebook')) {
                if (notebook.closest(".o_field_widget")) {
                    continue;
                }
                const name = notebook.dataset.name;
                if (name in state) {
                    const navs = notebook.querySelectorAll(':scope .o_notebook_headers .nav-item');
                    const pages = notebook.querySelectorAll(':scope > .tab-content > .tab-pane');
                    // We can't base the amount on the 'navs' length since some overrides
                    // are adding pageless nav items.
                    const validTabsAmount = pages.length;
                    if (!validTabsAmount) {
                        continue; // No page defined on the notebook.
                    }
                    let activeIndex = state[name];
                    if (navs[activeIndex].classList.contains('o_invisible_modifier')) {
                        activeIndex = [...navs].findIndex(
                            nav => !nav.classList.contains('o_invisible_modifier')
                        );
                    }
                    if (activeIndex <= 0) {
                        continue; // No visible tab OR first tab = active tab (no change to make).
                    }
                    for (let i = 0; i < validTabsAmount; i++) {
                        navs[i].querySelector('.nav-link').classList.toggle('active', activeIndex === i);
                        pages[i].classList.toggle('active', activeIndex === i);
                    }
                    $('.o_content').scrollTop(state.scrollTop);
                    setTimeout(function(){ $('.o_content').scrollTop(state.scrollTop); }, 1);
                    core.bus.trigger('DOM_updated');
                    console.log("Entra");
                }
            }

            console.log(state.scrollValue);
            $('.o_content').scrollTop(state.scrollTop);
            setTimeout(function(){ $('.o_content').scrollTop(state.scrollTop); }, 1);
            //  setTimeout(function(){ $('.o_content').scrollTop(state.scrollValue); }, 1);
        },

    });

});
