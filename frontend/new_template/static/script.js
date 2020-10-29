function update(){
        M.toast({html:'Update all your adress!!'});
        $.get("/update",
            function (data, textStatus, jqXHR) {
                M.toast({ html: data });
        });
    
}
function InfoPage(){
    render('#Info', '/info',
        function () {
            $('.tooltipped').tooltip();
            disabled = true;
            username = $('#id_username');
            last_val = username.val();
            username.on('change', function () {
                if (username.val() !== last_val) {
                    $('#submit_val').removeAttr('disabled');
                } else {
                    $('#submit_val').attr('disabled', 'true')
                }
            })
        }
    );
    render('#Table', 'tokenlist',
        function () {
            $('.tooltipped').tooltip();
            $('.modal').modal();
            $.map(document.querySelectorAll('.modal-trigger.address'), function (elementOrValue, i) {
                elementOrValue.onclick = function () {
                    $('#img').attr('src', "/share_token/" + elementOrValue.getAttribute('data-id'));
                };
            });
            $('.modal').modal();
            $.map(document.querySelectorAll('.modal-trigger.transaction'), function (elementOrValue, i) {
                elementOrValue.onclick = function () {
                    id = elementOrValue.getAttribute('data-id')
                    $('#form-transaction').attr('action', '/new_transaction/' + id);
                    addr = $('.token-value-' + id).html();
                    document.querySelector('#token-name').innerHTML = addr;

                };
            });
        }
    );

    $('#new_adress').on('click', function () {
        $.get("/new_token", undefined,
            function (data, textStatus, jqXHR) {
                M.toast({
                    html: 'new adress created:' + data
                });
            },
        );
    }
    )
}
function root(button,link,container) {
    
}

$(document).ready(function () {

    $('#update').on('click', function () {
        update();
    });
    render('#Navbar', '/static/component/navbar.htm',
        function () {
            $('.dropdown-trigger').dropdown({
                constrainWidth: false,
                coverTrigger: false,
                alignment: 'right'
            });
        }
    );
    render('#Sidebar', '/static/component/sidebar.htm',
        function () {
            $('.item-sidebar>a').on('mouseenter', function () {
                $('.sidebar').width(200);
            });
            $('.item-sidebar>a').on('mouseleave', function () {
                $('.sidebar').width(64);
            });
                
            $("li#InfoPage").click(function (e) {
                e.preventDefault();
                console.log('hello');
                render('#Container', 'static/component/page_info.html', function () {
                    InfoPage();
                });
            });
        }
    );
    $('.tooltipped').tooltip();
    $('.fixed-action-btn').floatingActionButton();
    
});