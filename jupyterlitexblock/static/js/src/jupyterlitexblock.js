/* Javascript for JupterLiteXBlock. */
function JupterLiteXBlock(runtime, element) {
  var getCompletionDelayUrl = runtime.handlerUrl(
    element,
    "get_completion_delay_seconds"
  );
  var markCompleteUrl = runtime.handlerUrl(element, "mark_complete");

  function checkCompletion(delaySeconds) {
    setTimeout(function () {
      $.ajax({
        type: "POST",
        url: markCompleteUrl,
        data: JSON.stringify({}),
        success: function (response) {
          if (response.result === "success") {
          }
        },
      });
    }, delaySeconds * 1000);
  }

  function getCompletionDelay() {
    $.ajax({
      type: "POST",
      url: getCompletionDelayUrl,
      data: JSON.stringify({}),
      contentType: "application/json",
      dataType: "json",
      success: function (data) {
        var delaySeconds = data.delay;
        checkCompletion(delaySeconds);
      },
    });
  }

  $(function ($) {
    getCompletionDelay();
  });

  $(element)
    .find(".save-button")
    .bind("click", function (event) {
      console.log("Strted JupterLiteXBlock");
      event.preventDefault();
      var formData = new FormData();
      var jupyterliteUrl = $(element).find("input[name=jupyterlite_url]").val();
      var default_notebook = $(element)
        .find("#default_notebook")
        .prop("files")[0];
      formData.append("jupyterlite_url", jupyterliteUrl);
      formData.append("default_notebook", default_notebook);

      runtime.notify("save", {
        state: "start",
      });
      $(this).addClass("disabled");
      $.ajax({
        url: runtime.handlerUrl(element, "studio_submit"),
        dataType: "json",
        cache: false,
        processData: false,
        contentType: false,
        data: formData,
        type: "POST",
        complete: function () {
          $(this).removeClass("disabled");
        },
        success: function (response) {
          if (response.errors.length > 0) {
            response.errors.forEach(function (error) {
              runtime.notify("error", {
                message: error,
                title: "Form submission error",
              });
            });
          } else {
            runtime.notify("save", { state: "end" });
          }
        },
      });
    });

  $(element)
    .find(".cancel-button")
    .on("click", function () {
      runtime.notify("cancel", {});
    });
}
