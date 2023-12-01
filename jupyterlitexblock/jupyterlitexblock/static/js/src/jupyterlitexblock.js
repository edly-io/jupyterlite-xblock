/* Javascript for JupterLiteXBlock. */
function JupterLiteXBlock(runtime, element) {

    $(element).find('.save-button').on('click', function () {
        var formData = new FormData();
        var jupyterliteUrl = $(element).find('input[name=jupyterlite_url]').val();
        var default_notebook = $(element).find('#default_notebook').prop('files')[0];
        formData.append('jupyterlite_url', jupyterliteUrl);
        formData.append('default_notebook', default_notebook);

        runtime.notify('save', {
            state: 'start'
        });
        // Make an AJAX request to the handlerUrl
        $(this).addClass("disabled");
        $.ajax({
            url: runtime.handlerUrl(element, 'studio_submit'),
            dataType: 'json',
            cache: false,
            processData: false,      
            contentType: false,
            data: formData,
            type: 'POST',
            complete: function () {
                $(this).removeClass("disabled");
            },
            success: function (response) {
                if (response.errors.length > 0) {
                    response.errors.forEach(function (error) {
                        runtime.notify('error', {
                            "message": error,
                            "title": 'Form submission error'
                        });
                    });
                } else {
                    runtime.notify('save', { state: 'end' });
                }
            },
        });
    });

    $(element).find('.cancel-button').on('click', function () {
        runtime.notify('cancel', {});
    });
}
