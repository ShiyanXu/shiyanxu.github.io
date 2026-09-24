// Shiyan's Notes — 站点脚本
document.addEventListener('DOMContentLoaded', function () {
  // 页脚年份
  var yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  // 文章列表页：按分类筛选
  var chipRow = document.getElementById('filter-chips');
  if (!chipRow) return;

  var chips = chipRow.querySelectorAll('.chip-btn');
  var rows = document.querySelectorAll('.post-row[data-category]');
  var yearLabels = document.querySelectorAll('.year-label');

  chipRow.addEventListener('click', function (e) {
    var btn = e.target.closest('.chip-btn');
    if (!btn) return;

    chips.forEach(function (c) { c.classList.remove('active'); });
    btn.classList.add('active');

    var filter = btn.getAttribute('data-filter');
    rows.forEach(function (row) {
      var show = filter === 'all' || row.getAttribute('data-category') === filter;
      row.classList.toggle('hidden', !show);
    });

    // 隐藏没有可见文章的年份分组标题
    yearLabels.forEach(function (label) {
      var el = label.nextElementSibling;
      var hasVisible = false;
      while (el && !el.classList.contains('year-label')) {
        if (el.classList.contains('post-row') && !el.classList.contains('hidden')) {
          hasVisible = true;
          break;
        }
        el = el.nextElementSibling;
      }
      label.classList.toggle('hidden', !hasVisible);
    });
  });
});
