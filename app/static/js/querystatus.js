function initPage() {
        $('.status').bootstrapSwitch();
        $(".status").on("switchChange.bootstrapSwitch", function (event, state) {
            switchStatus($(this).data("id"), state, this);
        });
    }

    //日期范围选择
    layui.use('laydate', function() {
        var laydate = layui.laydate;
        lay('.layui-input').each(function (){

            laydate.render({
                elem: this
                ,min: -30
                ,max: 0
                ,format: 'yyyy/MM/dd'
                ,range: true //或 range: '~' 来自定义分割字符
                ,trigger: 'click'
            });
        })
    });

    //提交模态框数据
    function pyecharts(elem) {
        var form = elem.value
        $.ajax({
            type: "POST",
            datatype: "json",
            url: "/api/pyecharts",
            data: $('#'+form).serialize(),
            success: function (result) {
                    console.log(result);//打印服务端返回的数据(调试用)
                    $('#py'+form).html(result.myecharts)
                },
                error : function() {
                    alert("异常！");
                }
        });
    }

    // 提交开关组件数据
    function switchStatus(id, status, switchBox) {
        restTemplate("PUT", "/items/" + id + "/status/" + status, null, function () {
            $($(switchBox)).bootstrapSwitch("state", status);
        });
    }