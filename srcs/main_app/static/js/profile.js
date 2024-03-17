function previewImage() {
    const input = document.getElementById('imageInput');
    const image = document.getElementById('profileImage');

    if (input.files && input.files[0]) {
        const reader = new FileReader();

        reader.onload = function (e) {
            image.src = e.target.result;
        };
        reader.readAsDataURL(input.files[0]);
    }
}

function resetFormValidation(form) {
    form.querySelectorAll('.is-invalid').forEach((element) => {
        element.classList.remove('is-invalid');
    });

    form.querySelectorAll('.invalid-feedback').forEach((feedbackElement) => {
        feedbackElement.textContent = '';
    });

    alert = document.getElementById('generalError');
    alert.classList.add('fade')
    alert.classList.remove('show')
    alert.innerHTML = '';
}

function cancelFormButton() {
    console.log('inside');
    form = document.getElementById("edit_profile_form");
    resetFormValidation(form);
    form.reset();
    element = document.getElementById("edit_profile");
    var myCollapse = new bootstrap.Collapse(element);
    myCollapse.toggle();
}

function submitForm() {
    form = document.getElementById("edit_profile_form");

    resetFormValidation(form);

    const formData = new FormData(form);

    fetch('/edit_profile/', {
        method: 'POST',
        body: formData,
    })
        .then(response => response.json().then(data => ({ status: response.status, ok: response.ok, body: data })))
        .then(data => {
            if (data.ok) {
                form.reset();

                fetchMainContent('/topbar', 'topBar');

                element = document.getElementById("edit_profile");
                var myCollapse = new bootstrap.Collapse(element);
                myCollapse.toggle();

            } else {
                handleServerSideErrors(form, data.body);
            }
        })
        .catch(error => console.log('error: ' + error));
}

function handleServerSideErrors(form, errors) {
    Object.entries(errors).forEach(([field, messages]) => {
        const message = Array.isArray(messages) ? messages.join(' ') : messages;

        const input = form.querySelector(`[name="${field}"]`);
        if (input) {
            input.classList.add('is-invalid');

            const feedback = input.nextElementSibling;

            if (feedback && feedback.classList.contains('invalid-feedback')) {
                feedback.textContent = message;
            }
        } else {
            alert = document.getElementById('generalError');
            alert.classList.remove('fade')
            alert.classList.add('show')
            alert.innerHTML = message;
        }
    });
}
