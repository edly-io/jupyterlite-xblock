/* Javascript for JupterLiteXBlock. */
function JupterLiteXBlock(runtime, element, initArgs) {
  var markCompleteUrl = runtime.handlerUrl(element, "mark_complete");
  var refreshJupyterliteXblock = runtime.handlerUrl(
    element,
    "refresh_jupyterlite_xblock"
  );
  var completionDelaySeconds = initArgs.completion_delay_seconds;

  function refreshJupyterliteXblockHandler() {
    $.ajax({
      type: "POST",
      url: refreshJupyterliteXblock,
      data: JSON.stringify({}),
      success: function (response) {
        if (response.result === "success") {
          var iframeElement = $(element).find(".jupyterlite-xblock");
          if (iframeElement.length > 0 && response.notebook_url) {
            iframeElement.attr("src", response.notebook_url);
          }
        }
      },
    });
  }
  $(element)
    .find(".refresh-jupyterlite-xblock-btn")
    .on("click", function () {
      refreshJupyterliteXblockHandler();
    });

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

  $(function ($) {
    checkCompletion(completionDelaySeconds);
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
