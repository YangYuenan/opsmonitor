function initPage() {
        switch_value = $('#status')[0].checked
        $('#status').bootstrapSwitch({
            state: switch_value,
            onText: '启用',
            offText: '停用'
        });

    }