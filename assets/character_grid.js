// 角色网格交互（事件委托 + Gradio 桥接）
(function () {
    if (window.__characterGridOK) return;
    window.__characterGridOK = true;

    window.toggleCharacterSelection = function (characterId) {
        const input = document.querySelector('.js-character-id input');
        if (!input) { console.warn('[grid] .js-character-id input not found'); return; }
        input.value = String(characterId);
        input.dispatchEvent(new Event('input',  { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
    };

    window.changePage = function (direction) {
        const input = document.querySelector('.js-page-direction input');
        if (!input) { console.warn('[grid] .js-page-direction input not found'); return; }
        input.value = String(direction);
        input.dispatchEvent(new Event('input',  { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
    };

    document.addEventListener('click', function (e) {
        const row = e.target.closest('.character-row');
        if (!row) return;
        const checkbox = row.querySelector('.character-checkbox input[type="checkbox"]');
        if (!checkbox) return;
        if (e.target === checkbox) return;
        checkbox.checked = !checkbox.checked;
        const id = parseInt(row.dataset.characterId, 10);
        window.toggleCharacterSelection(id);
    });

    document.addEventListener('change', function (e) {
        if (!e.target.matches('.character-checkbox input[type="checkbox"]')) return;
        e.stopPropagation();
        const row = e.target.closest('.character-row');
        if (!row) return;
        const id = parseInt(row.dataset.characterId, 10);
        window.toggleCharacterSelection(id);
    });

    console.log('[character_grid.js] 事件委托已注册');
})();