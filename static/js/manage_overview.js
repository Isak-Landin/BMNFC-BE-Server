// On page load, store the original HTML for each modal
const originalEditUserModal = $('#edit-modal').html();
const originalAddUserModal = $('#add-user-modal').html();
const originalAddAdminModal = $('#add-admin-modal').html();
const originalEditAdminModal = $('#edit-admin-modal').html();


// © 2025 Isak Landin and Compliq IT AB. All rights reserved.
// Proprietary software. Unauthorized use is prohibited.

// Page setup and table initialization
$(document).ready(function () {

  resetModal(); // For initial reset of modals

  // Inloggade Användare table
  $('#logged-in-table').DataTable({
    pageLength: 10,
    lengthChange: false,
    columnDefs: [
      { orderable: false, targets: -1 }  // Disable sorting on last column (actions)
    ],
    language: {
      search: "Sök:",
      paginate: {
        next: "Nästa",
        previous: "Föregående"
      },
      info: "Visar _START_ till _END_ av _TOTAL_ användare",
      infoEmpty: "Inga användare hittades",
      zeroRecords: "Inga matchande användare"
    }
  });

  // Registrerade Användare table
  $('#registered-table').DataTable({
    pageLength: 10,
    lengthChange: false,
    columnDefs: [
      { orderable: false, targets: -1 }  // Disable sorting on last column (actions)
    ],
    language: {
      search: "Sök:",
      paginate: {
        next: "Nästa",
        previous: "Föregående"
      },
      info: "Visar _START_ till _END_ av _TOTAL_ användare",
      infoEmpty: "Inga användare hittades",
      zeroRecords: "Inga matchande användare"
    }
  });

}); // <-- closes document ready


// Function for edit user modal
function openEditModal(userId, name, tagId, location, isActive, isLoggedIn) {
  resetModal();
  $('#edit-user-id').val(userId);
  $('#edit-user-name').val(name);
  $('#edit-tag-id').val(tagId);
  $('#edit-user-location').val(location);
  $('#edit-user-active').prop('checked', isActive);
  $('#edit-user-logged-in').prop('checked', isLoggedIn);
  $('#edit-modal').removeClass('hidden');
}

function enableEdit(field) {
  $(`#edit-user-${field}-display`).addClass('hidden');
  $(`#edit-user-${field}`).removeClass('hidden');
}

// Function for add user modal
function openAddUserModal() {
  resetModal();
  $('#add-user-modal').removeClass('hidden');
}

// Function for add admin modal
function openAddAdminModal() {
  resetModal();
  $('#add-admin-modal').removeClass('hidden');
}

// Function for delete admin modal
let pendingAdminDeleteForm = null;

function confirmDeleteAdmin(button, username) {
  if (!confirm(`Är du säker på att du vill ta bort adminanvändaren "${username}"?`)) {
    return;
  }

  const form = button.closest('form');
  const url = form.action;
  const csrfToken = form.querySelector('input[name="csrf_token"]').value;

  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: `csrf_token=${encodeURIComponent(csrfToken)}`
  })
  .then(response => {
    if (!response.ok) throw new Error("Något gick fel.");
    return response.json();
  })
  .then(data => {
    if (data.success) {
      const row = form.closest('tr');
      row.remove();
    } else {
      alert(data.message || "Borttagningen misslyckades.");
    }
  })
  .catch(error => {
    alert("Ett fel uppstod vid borttagning: " + error.message);
  });
}


// Function to confirm deletion of registered user
function confirmDeleteRegisteredUser(button, username) {
  if (!confirm(`Är du säker på att du vill ta bort användaren "${username}"?`)) {
    return;
  }

  const form = button.closest('form');
  const url = form.action;
  const csrfToken = form.querySelector('input[name="csrf_token"]').value;

  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: `csrf_token=${encodeURIComponent(csrfToken)}`
  })
  .then(response => {
    if (!response.ok) throw new Error("Något gick fel.");
    return response.json();
  })
  .then(data => {
    if (data.success) {
      const row = form.closest('tr');
      row.remove();
    } else {
      alert(data.message || "Borttagningen misslyckades.");
    }
  })
  .catch(error => {
    alert("Ett fel uppstod vid borttagning: " + error.message);
  });
}

function performDeleteAdmin() {
  if (pendingAdminDeleteForm) {
    pendingAdminDeleteForm.submit();
  }
}

// Function for edit admin modal
function openEditAdminModal(adminId, username) {
  resetModal();
  document.getElementById('edit-admin-id').value = adminId;
  document.getElementById('edit-admin-username').value = username;
  document.getElementById('edit-admin-password').value = '';
  document.getElementById('edit-admin-password-confirm').value = '';
  document.getElementById('edit-admin-modal').classList.remove('hidden');
}

// Function to edit registered user
function updateUserRow(userId, name, tagId, location, isActive, isLoggedIn) {
  const row = $(`#registered-table tbody tr[data-user-id="${userId}"]`);
  if (row.length === 0) return;

  row.find('td:eq(0)').text(name);
  row.find('td:eq(1)').text(tagId);
  row.find('td:eq(3)').text(location || '-');
  row.find('td:eq(4)').text(isActive ? 'Ja' : 'Nej');
  row.find('td:eq(5)').text(isLoggedIn ? 'Ja' : 'Nej');
}

// Handle "Logga ut" button for logged-in users
$(document).on('click', '.logout-user-btn', function () {
  const userId = $(this).data('user-id');
  const userName = $(this).data('user-name');
  const csrfToken = $('meta[name="csrf-token"]').attr('content');

  if (!confirm(`Vill du logga ut ${userName}?`)) return;

  $.ajax({
    url: `/manage/logout_user/${userId}`,
    method: 'POST',
    headers: {
      'X-CSRFToken': csrfToken
    },
    success: function (res) {
      if (res.success && res.user_id) {
        $(`#logged-in-table tbody tr[data-user-id="${res.user_id}"]`).remove();

        const regRow = $(`#registered-table tbody tr[data-user-id="${res.user_id}"]`);
        if (regRow.length) {
          regRow.find('td:eq(5)').text('Nej');
        }
      } else {
        alert('Misslyckades med att logga ut användaren.');
      }
    },
    error: function (xhr) {
      const message = xhr.responseJSON?.message || "Ett fel uppstod vid utloggning.";
      alert(message);
    }
  });
});

// Function to close modals
function closeModal(modalId = null) {
  if (modalId) {
    $(`#${modalId}`).addClass('hidden');
  } else {
    $('.modal-overlay').addClass('hidden');
  }
  resetModal();
}

// Function to reset modals
function resetModal() {
  $('#add-admin-form')[0].reset();
  $('#add-admin-message').addClass('hidden').removeClass('error success info warning').text('');
  $('#add-admin-modal').html(originalAddAdminModal);
  bindAddAdminModal();

  $('#edit-admin-form')[0].reset();
  $('#edit-admin-message').addClass('hidden').removeClass('error success info warning').text('');
  $('#edit-admin-modal').html(originalEditAdminModal);
  bindEditAdminModal();

  $('#add-user-form')[0].reset();
  $('#add-user-message').addClass('hidden').removeClass('error success info warning').text('');
  $('#add-user-modal').html(originalAddUserModal);
  bindAddUserModal();

  $('#edit-user-form')[0].reset();
  $('#edit-user-message').addClass('hidden').removeClass('error success info warning').text('');
  $('#edit-modal').html(originalEditUserModal);
  bindEditUserModal();
}



function bindEditUserModal() {
  // Handle edit user form submission via AJAX
  $('#edit-user-form').on('submit', function (e) {
    e.preventDefault();

    const userId = $('#edit-user-id').val();
    const name = $('#edit-user-name').val();
    const tagId = $('#edit-tag-id').val();
    const userLocation = $('#edit-user-location').val();
    const isActive = $('#edit-user-active').is(':checked');
    const isLoggedIn = $('#edit-user-logged-in').is(':checked');
    const csrfToken = $('meta[name="csrf-token"]').attr('content');

    const messageContainer = $('#edit-user-message');
    messageContainer.removeClass('error success info warning hidden').text('');
    messageContainer.addClass('hidden');

    $.ajax({
      url: `/manage/edit/${userId}`,
      method: 'POST',
      contentType: 'application/json',
      headers: { 'X-CSRFToken': csrfToken },
      data: JSON.stringify({
        name,
        tag_id: tagId,
        location: userLocation,
        is_active: isActive,
        is_logged_in: isLoggedIn
      }),
      success: function (response) {
        if (response.success) {
          messageContainer.addClass('success').text(response.message || 'Uppdateringen lyckades.');
          messageContainer.removeClass('hidden');
          setTimeout(() => closeModal('edit-modal'), 1000);
        } else {
          messageContainer.addClass('error').text(response.message || 'Uppdateringen misslyckades.');
          messageContainer.removeClass('hidden');
        }
      },
      error: function (xhr) {
        const message = xhr.responseJSON?.message || "Något gick fel vid uppdateringen.";
        messageContainer.addClass('error').text(message);
        messageContainer.removeClass('hidden');
      }
    });
  });
}

function bindAddUserModal() {
  // Handle add user form submission via AJAX
  $('#add-user-form').on('submit', function (e) {
    e.preventDefault();

    const name = $('#new-name').val().trim();
    const tagId = $('#new-tag-id').val().trim();
    const userLocation = $('#new-location').val();
    const isActive = $('#add-user-modal input[name="is_active"]').is(':checked');
    const isLoggedIn = $('#add-user-modal input[name="is_logged_in"]').is(':checked');
    const csrfToken = $('meta[name="csrf-token"]').attr('content');

    const messageContainer = $('#add-user-message');
    messageContainer.removeClass('error success info warning hidden').text('');
    messageContainer.addClass('hidden');

    if (!name || !tagId) {
      messageContainer.addClass('error').text("Både namn och tagg-ID krävs.");
      messageContainer.removeClass('hidden');
      return;
    }

    $.ajax({
      url: '/manage/add_user',
      method: 'POST',
      data: {
        name,
        tag_id: tagId,
        location: userLocation,
        is_active: isActive,
        is_logged_in: isLoggedIn,
        csrf_token: csrfToken
      },
      success: function (response) {
        if (response.success) {
          messageContainer.addClass('success').text(response.message || 'Användare tillagd.');
          messageContainer.removeClass('hidden');
          setTimeout(() => closeModal('add-user-modal'), 1000);
          location.reload();
        } else {
          messageContainer.addClass('error').text(response.message || 'Kunde inte lägga till användare.');
          messageContainer.removeClass('hidden');
        }
      },
      error: function (xhr) {
        const message = xhr.responseJSON?.message || "Ett fel uppstod.";
        messageContainer.addClass('error').text(message);
        messageContainer.removeClass('hidden');
      }
    });
  });
}

function bindAddAdminModal() {
  // Handle add admin form submission via AJAX
  $('#add-admin-form').on('submit', function (e) {
    e.preventDefault();

    const username = $('#admin-username').val().trim();
    const password = $('#admin-password').val().trim();
    const passwordConfirm = $('#admin-password-confirm').val().trim();
    const csrfToken = $('meta[name="csrf-token"]').attr('content');

    const messageContainer = $('#add-admin-message');
    messageContainer.removeClass('error success info warning hidden').text('');
    messageContainer.addClass('hidden');

    // Client-side validation
    if (username === "" || password === "") {
      messageContainer.addClass('error').text("Användarnamn och lösenord krävs.");
      messageContainer.removeClass('hidden');
      return;
    }

    if (password !== passwordConfirm) {
      messageContainer.addClass('error').text("Lösenorden matchar inte.");
      messageContainer.removeClass('hidden');
      return;
    }

    if (password.length < 6) {
      messageContainer.addClass('error').text("Lösenordet måste vara minst 6 tecken långt.");
      messageContainer.removeClass('hidden');
      return;
    }

    $.post({
      url: '/manage/add_admin',
      data: {
        username,
        password,
        csrf_token: csrfToken
      },
      success: function (response) {
        if (response.success) {
          messageContainer.addClass('success').text(response.message || 'Användare tillagd.');
          messageContainer.removeClass('hidden');
          setTimeout(() => closeModal('add-admin-modal'), 1000);
          location.reload();
        } else {
          messageContainer.addClass('error').text(response.message || 'Kunde inte lägga till användare.');
          messageContainer.removeClass('hidden');
        }
      },
      error: function (xhr) {
        const message = xhr.responseJSON?.message || "Ett fel uppstod.";
        messageContainer.addClass('error').text(message);
        messageContainer.removeClass('hidden');
      }
    });
  });
}





function bindEditAdminModal(){
    $('#edit-admin-form').on('submit', function (e) {
        e.preventDefault();

        const adminId = $('#edit-admin-id').val().trim();
        const username = $('#edit-admin-username').val().trim();
        const password = $('#edit-admin-password').val().trim();
        const passwordConfirm = $('#edit-admin-password-confirm').val().trim();
        const csrfToken = $('meta[name="csrf-token"]').attr('content');

        const messageContainer = $('#edit-admin-message');
        messageContainer.removeClass('info success warning error').text('');

        if (password !== passwordConfirm){
            messageContainer.addClass('error').text("Lösenorden matchar inte.");
            messageContainer.removeClass('hidden');
            return;
        }

        if (!username) {
            messageContainer.addClass('error').text("Användarnamn krävs.");
            messageContainer.removeClass('hidden');
            return;
        }

        if (password && password.length < 6){
            messageContainer.removeClass('hidden');
            messageContainer.addClass('error').text("Lösenordet måste vara minst 6 tecken långt.");
            return;
        }

        $.ajax({
            url: `/manage/edit_admin/${adminId}`,
            method: 'POST',
            contentType: 'application/json',
            headers: { 'X-CSRFToken': csrfToken },
            data: JSON.stringify({
                username: username,
                password: password
            }),
            success: function (response) {
                if (response.success === true) {
                    messageContainer
                        .removeClass('info warning error hidden')
                        .addClass('success')
                        .text(response.message || 'Adminuppdatering lyckades.');
                    setTimeout(() => closeModal(), 1500);
                } else {
                    messageContainer
                        .removeClass('info success warning hidden')
                        .addClass('error')
                        .text(response.message || 'Uppdateringen misslyckades.');
                        return;
                }
            },
            error: function (xhr) {
                const message = xhr.responseJSON?.message || "Ett fel uppstod.";
                messageContainer
                  .removeClass('info success warning error hidden')  // Clean all states
                  .addClass('error')                                 // Add error class
                  .text(message);
                  return;
            }
        });
    });
}

// © 2025 Isak Landin and Compliq IT AB. All rights reserved.
// Proprietary software. Unauthorized use is prohibited.
