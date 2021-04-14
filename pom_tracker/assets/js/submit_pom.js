$(document).ready(function () {
    $('form.pom-form').on('submit', function (e) {
        e.preventDefault();
    });
});

function submitPom() {

    let data = $('form.pom-form').serialize();
    // Validate the pom info
    $.ajax({
        url: '/pomodoro/submit',
        type: 'POST',
        cache: false,
        dataType: 'html',
        contentType: 'application/x-www-form-urlencoded',
        data: data,

        success: function (data, textStatus, jqXHR) {
            location.reload();
        },

        error: function (jqXHR, textStatus, errorThrown) {
            let error_data = null;
            let error_message = '';

            try {
                error_data = $.parseJSON(jqXHR.responseText).detail;
            } catch ($exception) {
                // Do nothing
            }

            if (error_data && Array.isArray(error_data)) {
                error_message = 'Missing required fields: ';
                error_data.forEach(element => error_message += (element['loc'][1] + ', '));
                error_message = error_message.trim();
                error_message = error_message.substring(0, error_message.length - 1);
                error_message = error_message.replace('_', ' ');
            } else if (typeof error_data == 'string') {
                error_message = error_data;
            }

            error_message = error_message ? error_message : errorThrown;

            $('#validation-error').text('Oops! ' + error_message).show();
        }
    });
}