function addPostShortcode() {
    let container = document.getElementById("post-shortcodes");

    const existingInputs = container.querySelectorAll('input[id^="shortcode"]');
    newId = `shortcode_${existingInputs.length + 1}`;


    const label = document.createElement('label')
    label.setAttribute('for', newId);
    label.textContent = `Post Shortcode #${existingInputs.length + 1}`;

    const input = document.createElement('input');
    input.type = 'text';
    input.name = newId;
    input.id = newId;
    input.required = true;

    const formGroup = document.createElement('div');
    formGroup.className = 'form-group';
    formGroup.appendChild(label);
    formGroup.appendChild(input);

    container.appendChild(formGroup);
}