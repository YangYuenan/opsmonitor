function initPage() {
        $('.status').bootstrapSwitch();
        $(".status").on("switchChange.bootstrapSwitch", function (event, state) {
            switchStatus($(this).data("id"), state, this);
        });
    }
    function switchStatus(id, status, switchBox) {
        restTemplate("PUT", "/notifies/" + id + "/status/" + status, null, function () {
            $($(switchBox)).bootstrapSwitch("state", status);
        });
    }