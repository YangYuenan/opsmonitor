function initPage() {

        switch_value = $('#status')[0].checked
        $('#status').bootstrapSwitch({
            state: switch_value,
            onText: '生效',
            offText: '失效'

        });

        $(".select2").select2();
    }