// Python does the math. This file edits courses, saves them, and shows results.
const $ = id => document.getElementById(id);
const grades = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F', 'P', 'W', 'I'];
const levels = ['Regular', 'Honors', 'AP / IB'];
const storageKey = 'python-gpa-v1';
const newCourse = () => ({ name: '', grade: '', credits: 5, level: 'Regular' });
const newSemester = () => ({ weighted: true, courses: [newCourse(), newCourse(), newCourse()] });
const formatGpa = value => value === null ? '—' : value.toFixed(2);
let state = { semesters: [newSemester()] };
let latestRequest = 0;

// Keep existing coursework when the app is reopened.
try {
  const saved = JSON.parse(localStorage.getItem(storageKey));
  if (saved && Array.isArray(saved.semesters) && saved.semesters.every(semester =>
    semester && Array.isArray(semester.courses) && semester.courses.every(course =>
      course && typeof course.name === 'string'))) {
    state = saved;
  }
} catch { /* Start fresh if browser storage is unavailable. */ }

function fillOptions(select, options, value) {
  for (const option of options) select.add(new Option(option || 'Grade', option));
  select.value = value;
}

// Templates keep HTML separate from the application logic.
function render() {
  $('semesters').replaceChildren();
  state.semesters.forEach((semester, semesterIndex) => {
    const card = $('semester-template').content.firstElementChild.cloneNode(true);
    card.dataset.semester = semesterIndex;
    card.querySelector('h3').textContent = `Semester ${semesterIndex + 1}`;
    card.querySelector('[data-action="weight"]').checked = semester.weighted;

    semester.courses.forEach((course, courseIndex) => {
      const row = $('course-template').content.firstElementChild.cloneNode(true);
      row.dataset.course = courseIndex;
      row.querySelector('[data-field="name"]').value = course.name;
      row.querySelector('[data-field="credits"]').value = course.credits;
      fillOptions(row.querySelector('[data-field="grade"]'), ['', ...grades], course.grade);
      const level = row.querySelector('[data-field="level"]');
      fillOptions(level, levels, course.level);
      level.disabled = !semester.weighted;
      card.querySelector('.rows').append(row);
    });
    $('semesters').append(card);
  });
}

// One input handler serves every course and semester.
$('semesters').addEventListener('input', event => {
  const input = event.target;
  const card = input.closest('.semester');
  const semester = state.semesters[card.dataset.semester];
  if (input.dataset.action === 'weight') {
    semester.weighted = input.checked;
    card.querySelectorAll('[data-field="level"]').forEach(select => {
      select.disabled = !semester.weighted;
    });
  } else if (input.dataset.field) {
    const course = semester.courses[input.closest('.course').dataset.course];
    course[input.dataset.field] = input.value;
  }
  update();
});

$('semesters').addEventListener('click', event => {
  const button = event.target.closest('button');
  if (!button) return;
  const card = button.closest('.semester');
  const index = Number(card.dataset.semester);
  const courses = state.semesters[index].courses;

  switch (button.dataset.action) {
    case 'add-course':
      courses.push(newCourse());
      break;
    case 'remove-course':
      courses.splice(Number(button.closest('.course').dataset.course), 1);
      break;
    case 'remove-semester':
      if (!confirm('Remove this semester and its courses?')) return;
      state.semesters.splice(index, 1);
      break;
  }
  render();
  update();
  if (button.dataset.action === 'add-course') {
    $('semesters').children[index].querySelector('.rows').lastElementChild.querySelector('input').focus();
  }
});

function showResults(result) {
  $('overall').textContent = formatGpa(result.gpa);
  $('unweighted').textContent = formatGpa(result.unweighted);
  $('credits').textContent = result.credits ?? '—';
  document.querySelectorAll('.value').forEach((element, index) => {
    element.textContent = formatGpa(result.semesters[index]?.gpa ?? null);
  });
}

async function update() {
  try {
    localStorage.setItem(storageKey, JSON.stringify(state));
  } catch {
    $('saved').textContent = 'Browser saving unavailable';
  }

  // Older responses must not overwrite a newer edit.
  const request = ++latestRequest;
  $('status').textContent = 'Calculating…';
  try {
    const response = await fetch('/api/calculate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(state)
    });
    const result = await response.json();
    if (request !== latestRequest) return;
    if (!response.ok) throw new Error(result.error);
    showResults(result);
    $('status').textContent = '';
  } catch (error) {
    if (request !== latestRequest) return;
    showResults({ gpa: null, unweighted: null, credits: null, semesters: [] });
    $('status').textContent = error.message === 'Failed to fetch'
      ? 'Start the Python server to calculate your GPA.' : error.message;
  }
}

$('add-semester').onclick = () => {
  state.semesters.push(newSemester());
  render();
  update();
  $('semesters').lastElementChild.scrollIntoView({ behavior: 'smooth' });
};

$('reset').onclick = () => {
  if (!confirm('Clear all coursework?')) return;
  state = { semesters: [newSemester()] };
  render();
  update();
};

const points = [4, 4, 3.7, 3.3, 3, 2.7, 2.3, 2, 1.7, 1.3, 1, 0.7, 0];
grades.forEach((grade, index) => {
  const label = document.createElement('span');
  label.textContent = `${grade}: ${points[index] ?? 'excluded'}`;
  $('scale').append(label);
});

render();
update();
