$(function () {
    $("#input-group-button-right").on("click", async () => {
        let search_word = $("#search_word").val();
        if (!search_word) {
            alert("検索ワードを入力してください。");
            return;
        }
        else {
            $("#input-group-button-right").hide();
            $('#tuika').append('<button type="button" id="loading_button" class="btn btn-primary" type="button" disabled><span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>Loading...</button>');
            await eel.fetch_data(search_word = search_word)
        }
    });
});

eel.expose(enable_btn)
function enable_btn() {
    $("#loading_button").remove();
    $("#input-group-button-right").show();
}

eel.expose(output_oder_list)
function output_oder_list(text) {
    let output_text = $("#output-data").val() + text + "\n";
    $("#output-data").val(output_text);
    $("#output-data").scrollTop($("#output-data")[0].scrollHeight);
}

// eel.expose(reset_object)
// function reset_object() {
//     document.order_form.reset();
// }

eel.expose(alert_js)
function alert_js(text) {
    alert(text);
}