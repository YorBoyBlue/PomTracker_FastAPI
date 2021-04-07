$(document).ready(function () {
    $('form.pom-form').on('submit', function (e) {
        e.preventDefault();
    });
});

function submitPom() {

    let data = $('form.pom-form').serialize();
    // Validate the pom info
    $.ajax({
        url: '/api/pom_validation',
        type: 'POST',
        cache: false,
        dataType: 'html',
        contentType: 'application/x-www-form-urlencoded',
        data: data,

        success: function (data, textStatus, jqXHR) {
            // Pom is valid, try to submit pom to DB
            let form_data = $('form.pom-form').serialize();
            $.ajax({
                url: '/api/poms/today',
                type: 'POST',
                cache: false,
                dataType: 'html',
                contentType: 'application/x-www-form-urlencoded',
                data: form_data,

                success: function (data, textStatus, jqXHR) {
                    location.reload();
                },

                error: function (jqXHR, textStatus, errorThrown) {

                    // console.log(data);
                    // console.log(textStatus);
                    // console.log(jqXHR.responseText);
                    let error_data = $.parseJSON(jqXHR.responseText).title;
                    $.ajax({
                        url: '/app/pom_exists',
                        type: 'POST',
                        cache: false,
                        dataType: 'html',
                        contentType: 'application/json',
                        processData: false,
                        data: JSON.stringify(error_data.data),

                        success: function (data, textStatus, jqXHR) {
                            $('form.pom-form').replaceWith(data);
                        },

                        error: function (jqXHR, textStatus, errorThrown) {
                        }
                    });
                }
            });
        },

        error: function (jqXHR, textStatus, errorThrown) {
            let error_data = $.parseJSON(jqXHR.responseText).title;
            $.ajax({
                url: '/app/pom_invalid',
                type: 'POST',
                cache: false,
                dataType: 'html',
                contentType: 'application/json',
                processData: false,
                data: JSON.stringify(error_data.data),

                success: function (data, textStatus, jqXHR) {
                    $('form.pom-form').replaceWith(data);
                },

                error: function (jqXHR, textStatus, errorThrown) {
                }
            });
        }
    });
}

function replacePom() {
    let data = $('form.pom-form').serialize();
    $.ajax({
        url: '/api/pom_replace',
        type: 'POST',
        cache: false,
        dataType: 'html',
        contentType: 'application/x-www-form-urlencoded',
        data: data,
        success: function (data, textStatus, jqXHR) {
            // Runs only when a 200 OK is returned
            // Reload page when pom was submitted successfully
            location.reload();
        },
        error: function (jqXHR, textStatus, errorThrown) {
            // Runs when any error is returned

            let error_data = $.parseJSON(jqXHR.responseText).title;
            if (error_data.error === 'ValidationError') {
                $.ajax({
                    url: '/app/pom_exists',
                    type: 'POST',
                    cache: false,
                    dataType: 'html',
                    contentType: 'application/json',
                    processData: false,
                    data: JSON.stringify(error_data.data),
                    success: function (data, textStatus, jqXHR) {
                        // Runs only when a 200 OK is returned
                        $('form.pom-form').replaceWith(data);
                        // console.log('success');
                    },
                    error: function (jqXHR, textStatus, errorThrown) {
                        console.log('error');
                    }
                });
            }
        },
        complete: function (jqXHR, textStatus) {
            // Runs whether or not an error is returned
        }
    });
}