function initPage() {
        var jsInObj = null;
        restTemplate("GET", "/stats/summary", jsInObj, function (jsOutObj) {
            $("#count01").text(jsOutObj.host_count);
            $("#count02").text(jsOutObj.item_count);
            $("#count03").text(jsOutObj.danger_count);
        });
        host_pyecharts();
        item_pyecharts();
    }

    //提交模态框数据
    function item_pyecharts() {
        $.ajax({
            type: "GET",
            url: "/api/item/warning",
            success: function (result) {
                    console.log(result);//打印服务端返回的数据(调试用)
                    $('#item-trend').html(result.myecharts)
                },
                error : function() {
                    alert("异常！");
                }
        });
    }
    function host_pyecharts() {
        $.ajax({
            type: "GET",
            url: "/api/host/warning",
            success: function (result) {
                    console.log(result);//打印服务端返回的数据(调试用)
                    $('#host-trend').html(result.myecharts)
                },
                error : function() {
                    alert("异常！");
                }
        });
    }