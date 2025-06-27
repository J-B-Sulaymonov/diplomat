// ===================================================================================
// ASINXRON FUNKSIYALAR: Bog'liq menyular uchun ma'lumotlarni yuklash
// ===================================================================================

/**
 * Tanlangan darajaga mos ta'lim yo'nalishlarini serverdan yuklaydi.
 * @param {string} degreeId - Tanlangan darajaning ID'si.
 */
async function loadDirections(degreeId) {
    const directionSelect = document.getElementById('education-direction');
    const studyFormSelect = document.getElementById('study-form');

    // Yo'nalish va ta'lim shakli select'larini reset qilish
    directionSelect.innerHTML = '<option value="">{% trans "Loading..." %}</option>';
    directionSelect.disabled = true;
    studyFormSelect.innerHTML = '<option value="">{% trans "Choose a direction first." %}</option>';
    studyFormSelect.disabled = true;

    if (!degreeId) {
        directionSelect.innerHTML = '<option value="">{% trans "First select the level" %}</option>';
        return;
    }

    try {
        const response = await fetch(`/ajax/get-directions/${degreeId}/`);
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();

        directionSelect.innerHTML = '<option value="">---------</option>';
        data.forEach(direction => {
            const option = new Option(direction.name, direction.id);
            directionSelect.add(option);
        });
        directionSelect.disabled = false;
    } catch (error) {
        console.error('{% trans "Error loading training courses:" %}', error);
        directionSelect.innerHTML = '<option value="">{% trans "An error occurred." %}</option>';
    }
}

/**
 * Tanlangan yo'nalishga mos ta'lim shakllarini serverdan yuklaydi.
 * @param {string} directionId - Tanlangan yo'nalishning ID'si.
 */
async function loadStudyForms(directionId) {
    const studyFormSelect = document.getElementById('study-form');
    studyFormSelect.innerHTML = '<option value="">{% trans "Loading..." %}</option>';
    studyFormSelect.disabled = true;

    if (!directionId) {
        studyFormSelect.innerHTML = '<option value="">{% trans "Choose a direction first." %}</option>';
        return;
    }

    try {
        const response = await fetch(`/ajax/get-study-forms/${directionId}/`);
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();

        studyFormSelect.innerHTML = '<option value="">---------</option>';
        if (data.length > 0) {
            data.forEach(form => {
                const option = new Option(form.name, form.id);
                studyFormSelect.add(option);
            });
            studyFormSelect.disabled = false;
        } else {
            studyFormSelect.innerHTML = '<option value="">{% trans "No form of education available" %}</option>';
            studyFormSelect.disabled = true; // Ta'lim shakli bo'lmasa, disable qilish kerak
        }
    } catch (error) {
        console.error('{% trans "Error loading educational forms:" %}', error);
        studyFormSelect.innerHTML = '<option value="">{% trans "An error occurred." %}</option>';
    }
}

function saveFormState() {
    const form = document.getElementById('applicationForm');
    const elements = form.elements;
    const dataToStore = {};

    for (const element of elements) {
        if (element.name && element.type !== 'submit' && element.type !== 'button') {
            if (element.type === 'file') {
                if (element.files.length > 0) {
                    dataToStore[element.name] = { filename: element.files[0].name };
                }
            } else if (element.type === 'radio') {
                if (element.checked) {
                    dataToStore[element.name] = element.value;
                }
            } else {
                dataToStore[element.name] = element.value;
            }
        }
    }
    localStorage.setItem('applicationFormData', JSON.stringify(dataToStore));
}

/**
 * localStorage'dan saqlangan ma'lumotlarni formaga qayta yuklaydi.
 */
async function loadFormState() {
    const savedDataJSON = localStorage.getItem('applicationFormData');
    if (!savedDataJSON) return;

    const data = JSON.parse(savedDataJSON);
    const form = document.getElementById('applicationForm');

    // Oddiy maydonlarni to'ldirish
    for (const name in data) {
        if (form.elements[name]) {
            const element = form.elements[name];
            // Bog'liq select'larni alohida ishlaymiz
            const dependentFields = ['degree', 'education_direction', 'study_form'];
            if (dependentFields.includes(name)) continue;

            if (element.type === 'file') {
                const filename = data[name]?.filename;
                if (filename) {
                    let fileInfo = element.parentNode.querySelector('.file-info');
                    if (!fileInfo) {
                        fileInfo = document.createElement('span');
                        fileInfo.className = 'file-info text-muted small d-block';
                        element.parentNode.insertBefore(fileInfo, element.nextSibling);
                    }
                    fileInfo.innerHTML = `{% trans "Last selected file:" %} <strong>${filename}</strong>. <br>{% trans "For security reasons, you must reselect the file." %}`;
                }
            } else if (element.type === 'radio') {
                if (element.value === data[name]) {
                    element.checked = true;
                }
            } else {
                element.value = data[name];
            }
        }
    }

    // Bog'liq select'larni to'g'ri ketma-ketlikda yuklash
    if (data.degree) {
        form.elements['degree'].value = data.degree;
        await loadDirections(data.degree); // Yo'nalishlarni yuklashni kutamiz
    }
    if (data.education_direction) {
        form.elements['education_direction'].value = data.education_direction;
        await loadStudyForms(data.education_direction); // Ta'lim shakllarini yuklashni kutamiz
    }
    if (data.study_form) {
        form.elements['study_form'].value = data.study_form;
    }
     console.log('{% trans "The data was successfully reloaded." %}');
}

// ===================================================================================
// VALIDATSIYA YORDAMCHI FUNKSIYALARI
// ===================================================================================

/**
 * Belgilangan maydon ostida validatsiya xatosini ko'rsatadi.
 * @param {string} fieldId - Input maydonining ID'si.
 * @param {string} message - Ko'rsatiladigan xatolik xabari.
 */
function displayValidationError(fieldId, message) {
    const field = document.getElementById(fieldId);
    const errorElement = document.getElementById(`${fieldId}-error`); // Xato uchun element (masalan, <div id="passport-error">)
    if(field) field.classList.add('is-invalid');
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    }
}

/**
 * Formadagi barcha validatsiya xatoliklarini tozalaydi.
 */
function clearValidationErrors() {
    document.querySelectorAll('.invalid-feedback').forEach(el => {
        el.textContent = '';
        el.style.display = 'none';
    });
    document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
}

/**
 * Backend'ga murojaat qilib pasport va JSHIRning noyobligini tekshiradi.
 * @returns {Promise<boolean>} - Agar noyob bo'lsa true, aks holda false qaytaradi.
 */
async function checkUniqueness() {
    clearValidationErrors();

    const passportInput = document.getElementById('passport');
    const jshirInput = document.getElementById('jshir');
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    try {
        const response = await fetch('/api/check-uniqueness/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                passport: passportInput.value,
                jshir: jshirInput.value
            })
        });

        if (!response.ok) throw new Error('{% trans "An error occurred while connecting to the server." %}');

        const data = await response.json();

        if (data.is_unique) {
            return true;
        } else {
            if (data.errors.passport) {
                displayValidationError('passport', data.errors.passport);
            }
            if (data.errors.jshir) {
                displayValidationError('jshir', data.errors.jshir);
            }
            return false;
        }
    } catch (error) {
        console.error('{% trans "Error checking uniqueness:" %}', error);
        alert(error.message);
        return false;
    }
}

// ===================================================================================
// BOSQICHMA-BOSQICH FORMA (WIZARD) LOGIKASI
// ===================================================================================

let currentStep = 1;

/**
 * Bosqichlar o'rtasida o'tishni boshqaradi, validatsiyani tekshiradi.
 * @param {number} step - O'tish kerak bo'lgan bosqich raqami.
 */
async function goToStep(step) {
    // --- Keyingi bosqichga o'tishdan oldin validatsiya ---
    if (step > currentStep) {
        const currentStepContainer = document.getElementById('step-' + currentStep);
        const inputs = currentStepContainer.querySelectorAll('input[required], select[required]');

        let isBrowserValid = true;
        for (const input of inputs) {
            if (!input.reportValidity()) {
                isBrowserValid = false;
                input.classList.add('is-invalid');
            } else {
                input.classList.remove('is-invalid');
            }
        }

        if (!isBrowserValid) return; // Brauzerning oddiy validatsiyasidan o'tmasa, to'xtaymiz.

        // Agar 1-bosqichdan 2-bosqichga o'tayotgan bo'lsak, noyoblikni tekshiramiz.
        if (currentStep === 1 && step === 2) {
            const isUnique = await checkUniqueness();
            if (!isUnique) return; // Agar ma'lumotlar noyob bo'lmasa, to'xtaymiz.
        }
    }

    // --- Barcha bosqichlarni yashirish ---
    document.getElementById('step-1').style.display = 'none';
    document.getElementById('step-2').style.display = 'none';
    document.getElementById('step-3').style.display = 'none';
    document.getElementById('step-4').style.display = 'none';
    clearValidationErrors();

    // --- Kerakli bosqich(lar)ni ko'rsatish ---
    if (step === 3) {
        // Step 3 ga o'tishdan oldin 2-bosqich validatsiyasini tekshirish
        const step2Container = document.getElementById('step-2');
        const inputsStep2 = step2Container.querySelectorAll('input[required], select[required]');
        let isStep2Valid = true;
        for (const input of inputsStep2) {
            if (!input.reportValidity()) {
                isStep2Valid = false;
                break;
            }
        }

        if (!isStep2Valid) {
            document.getElementById('step-2').style.display = 'block'; // 2-bosqichni ko'rsatib,
            updateStepIndicator(2);                                   // shu yerda to'xtaymiz
            currentStep = 2;
            return;
        }

        // Agar 2-bosqich ham to'g'ri bo'lsa, 3-bosqichni tayyorlaymiz
        document.getElementById('step-1').style.display = 'block';
        document.getElementById('step-2').style.display = 'block';
        document.getElementById('step-3').style.display = 'block';

        document.querySelector('#step-1 .form-actions').style.display = 'none';
        document.querySelector('#step-2 .form-actions').style.display = 'none';

        const surname = document.getElementById('surname').value.trim();
        const firstName = document.getElementById('first_name').value.trim();
        const confirmationP = document.getElementById('confirmation-name-paragraph');
        if (confirmationP) {
            confirmationP.textContent = `I, ${surname} ${firstName},`;
        }
    } else {
         document.getElementById('step-' + step).style.display = 'block';
    }

    updateStepIndicator(step);
    currentStep = step;
}

/**
 * Yuqoridagi bosqich indikatorlarini yangilaydi.
 * @param {number} activeStep - Joriy faol bosqich raqami.
 */
function updateStepIndicator(activeStep) {
    for (let i = 1; i <= 4; i++) {
        const indicator = document.getElementById('step-indicator-' + i);
        if (!indicator) continue;
        const circle = indicator.querySelector('.step-circle');
        indicator.classList.remove('completed', 'active');

        if (i < activeStep) {
            indicator.classList.add('completed');
            circle.innerHTML = '<i class="fas fa-check"></i>';
        } else if (i === activeStep) {
            indicator.classList.add('active');
            circle.innerHTML = (i === 4) ? '<i class="fas fa-flag-checkered"></i>' : i;
        } else {
            circle.innerHTML = (i === 4) ? '<i class="fas fa-flag-checkered"></i>' : i;
        }
    }
}


// ===================================================================================
// SAHIFA YUKLANGANDA ISHGA TUSHADIGAN KOD (INITIALIZATION)
// ===================================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Saqlangan ma'lumotlarni yuklash
    loadFormState();

    const form = document.getElementById('applicationForm');

    // Har bir o'zgarishda formani saqlab borish
    form.addEventListener('input', saveFormState);

    // Bog'liq select'lar uchun event listener'lar
    document.getElementById('degree').addEventListener('change', function() {
        loadDirections(this.value);
    });

    document.getElementById('education-direction').addEventListener('change', function() {
        loadStudyForms(this.value);
    });

    // JSHIR maydoniga faqat raqam kiritishni ta'minlash
    const jshirInput = document.getElementById('jshir');
    if (jshirInput) {
        jshirInput.addEventListener('input', function(e) {
            e.target.value = e.target.value.replace(/[^0-9]/g, '');
        });
    }

    // Tasdiqlash checkbox'i va Submit tugmasi logikasi
    const confirmCheckbox = document.getElementById('confirm-checkbox');
    const submitBtn = document.getElementById('submit-btn');

    if (confirmCheckbox && submitBtn) {
        confirmCheckbox.addEventListener('change', function() {
            submitBtn.disabled = !this.checked;
        });
    }

    // Formani yuborish (submit) hodisasi
    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Sahifani yangilanishini to'xtatish
        if (confirmCheckbox && !confirmCheckbox.checked) {
            alert('{% trans "Please confirm the terms." %}');
            return;
        }

        // Bu yerda form ma'lumotlarini serverga yuborish uchun
        // haqiqiy AJAX so'rovini yozishingiz kerak bo'ladi.
        // Hozircha bu shunchaki 4-bosqichga o'tishni simulyatsiya qiladi.
        console.log('{% trans "Application submitted!" %}');

        document.getElementById('application-number').innerText = 'DU' + new Date().getTime();
        goToStep(4);
        localStorage.removeItem('applicationFormData'); // Ish tugagach, ma'lumotlarni tozalash
    });

    // Boshlang'ich holatni sozlash
    updateStepIndicator(1);

    // Validatsiya xabarlari uchun stillarni dinamik qo'shish
    const style = document.createElement('style');
    style.innerHTML = `
        .invalid-feedback {
            width: 100%;
            margin-top: .25rem;
            font-size: .875em;
            color: #dc3545;
            display: none; /* By default, hide error messages */
        }
        input.is-invalid, select.is-invalid {
            border-color: #dc3545 !important;
        }
    `;
    document.head.appendChild(style);
});

// script.js (faylning oxirgi qismi)

// ===================================================================================
// FAYL YUKLASH FUNKSIYASI
// ===================================================================================
/**
 * Ariza raqamini matn (.txt) fayli sifatida yuklab oladi.
 */
function downloadApplicationNumber() {
    const appNumberElement = document.getElementById('application-number');
    const appNumber = appNumberElement.innerText;

    if (!appNumber) {
        alert('{% trans "Application not found!" %}');
        return;
    }

    // Fayl kontenti
    const fileContent = `Sizning Diplomat Universitetiga topshirgan ariza raqamingiz: ${appNumber}`;

    // Faylni yaratish
    const blob = new Blob([fileContent], { type: 'text/plain;charset=utf-8' });

    // Yuklab olish uchun vaqtinchalik link yaratish
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `${appNumber}.txt`; // Fayl nomi

    document.body.appendChild(link);
    link.click(); // Linkni avtomatik bosish
    document.body.removeChild(link); // Linkni o'chirish
}


// ===================================================================================
// SAHIFA YUKLANGANDA ISHGA TUSHADIGAN KOD (INITIALIZATION)
// ===================================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Saqlangan ma'lumotlarni yuklash
    loadFormState();

    const form = document.getElementById('applicationForm');
    const submitBtn = document.getElementById('submit-btn');

    // Har bir o'zgarishda formani saqlab borish
    form.addEventListener('input', saveFormState);

    // Bog'liq select'lar uchun event listener'lar
    document.getElementById('degree').addEventListener('change', function() {
        loadDirections(this.value);
    });

    document.getElementById('education-direction').addEventListener('change', function() {
        loadStudyForms(this.value);
    });

    // JSHIR maydoniga faqat raqam kiritishni ta'minlash
    const jshirInput = document.getElementById('jshir');
    if (jshirInput) {
        jshirInput.addEventListener('input', function(e) {
            e.target.value = e.target.value.replace(/[^0-9]/g, '');
        });
    }

    // Tasdiqlash checkbox'i va Submit tugmasi logikasi
    const confirmCheckbox = document.getElementById('confirm-checkbox');
    if (confirmCheckbox && submitBtn) {
        confirmCheckbox.addEventListener('change', function() {
            submitBtn.disabled = !this.checked;
        });
    }

    // ==========================================================
    // YANGILANGAN FORMANI YUBORISH (SUBMIT) HODISASI
    // ==========================================================
    form.addEventListener('submit', async function(event) {
        event.preventDefault(); // Sahifani yangilanishini to'xtatish

        if (!confirmCheckbox.checked) {
            alert('{% trans "Please confirm the application." %}');
            return;
        }

        submitBtn.disabled = true;
        submitBtn.textContent = '{% trans "Sending..." %}';

        // Barcha forma ma'lumotlarini (fayllar bilan birga) yig'ish
        const formData = new FormData(form);
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

        try {
            const response = await fetch(form.action || window.location.pathname, { // Form action yoki joriy URL
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken
                    // 'Content-Type' kerak emas, brauzer FormData bilan o'zi qo'yadi
                },
                body: formData
            });

            const result = await response.json();

            if (response.ok && result.success) {
                // Muvaffaqiyatli javob
                document.getElementById('application-number').innerText = result.application_number;
                goToStep(4);
                localStorage.removeItem('applicationFormData'); // Ish tugagach, ma'lumotlarni tozalash
            } else {
                // Serverdan kelgan xatoliklar
                alert('{% trans "There was an error submitting the application. Please check the fields." %}');
                console.error('Server errors:', result.errors);
            }

        } catch (error) {
            // Tarmoq xatoliklari yoki boshqa kutilmagan xatolar
            console.error('Submit error:', error);
            alert('{% trans "An unexpected error occurred while submitting the application." %}');
        } finally {
            // Natijadan qat'iy nazar, tugmani asl holiga qaytarish
            submitBtn.disabled = false;
            submitBtn.textContent = 'SUBMIT';
        }
    });

    // "Ariza raqamini saqlash" tugmasiga event listener qo'shish
    const saveBtn = document.getElementById('save-app-number-btn');
    if (saveBtn) {
        saveBtn.addEventListener('click', downloadApplicationNumber);
    }

    // Boshlang'ich holatni sozlash
    updateStepIndicator(1);

    // Validatsiya xabarlari uchun stillarni dinamik qo'shish
    const style = document.createElement('style');
    style.innerHTML = `
        .invalid-feedback {
            width: 100%;
            margin-top: .25rem;
            font-size: .875em;
            color: #dc3545;
            display: none;
        }
        input.is-invalid, select.is-invalid {
            border-color: #dc3545 !important;
        }
    `;
    document.head.appendChild(style);
});