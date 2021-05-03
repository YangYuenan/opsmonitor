function initPage() {
        slide_value = $(".slider").val() == "" ? 5 : parseInt($(".slider").val());
        $(".slider").slider({
            id: "blue",
            min: 1,
            max: 10,
            value: slide_value
        });

    }