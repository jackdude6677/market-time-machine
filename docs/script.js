document.addEventListener('DOMContentLoaded', () => {
  const themeToggle = document.getElementById('theme-toggle');
  const root = document.documentElement;
  themeToggle.addEventListener('click', () => {
    const isDark = root.getAttribute('data-theme') === 'dark';
    root.setAttribute('data-theme', isDark ? 'light' : 'dark');
    themeToggle.textContent = isDark ? '🌙' : '☀️';
  });

  // Load demo data
  fetch('data/demo_snapshot.json')
    .then(r => r.json())
    .then(data => {
      document.getElementById('capital').textContent = `Capital: $${data.capital.toLocaleString()}`;
      document.getElementById('positions').textContent = `Positions: ${data.positions.join(', ') || 'None'}`;

      const gradesList = document.getElementById('grades-list');
      data.weekly_grades.forEach(g => {
        const li = document.createElement('li');
        li.textContent = `${g.week}: ${g.grade}`;
        gradesList.appendChild(li);
      });

      const stratList = document.getElementById('strategies-list');
      data.strategies.forEach(s => {
        const li = document.createElement('li');
        li.textContent = `${s.name} (survival: ${s.survival}%)`;
        stratList.appendChild(li);
      });

      const relList = document.getElementById('relationships-list');
      data.relationships.forEach(r => {
        const li = document.createElement('li');
        li.textContent = `${r.type}: ${r.detail}`;
        relList.appendChild(li);
      });

      const audList = document.getElementById('auditor-list');
      data.auditor_findings.forEach(f => {
        const li = document.createElement('li');
        li.textContent = f;
        audList.appendChild(li);
      });

      const commandsPre = document.getElementById('commands');
      data.commands.forEach(cmd => {
        const line = document.createElement('div');
        line.textContent = cmd;
        commandsPre.appendChild(line);
      });
    })
    .catch(err => {
      console.error('Failed to load demo data', err);
    });
});
