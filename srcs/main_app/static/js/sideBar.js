$(".friendName").parent(".friend").parent('.navigationBar').hover(
    function() {
           $('.friendName').css('width', '75%');
           $('.friendName').css('display', 'flex');
          }, function() {
            $('.friendName').css('width', '0px');
            $('.friendName').css('display', 'none');
          }
          );
