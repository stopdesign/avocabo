django.jQuery(function(){
  var input = django.jQuery('input[type=text]');
  input.attr('autocomplete', 'off');
  input.attr('autocorrect', 'off');
  input.attr('autocapitalize', 'off');
  input.attr('spellcheck', 'false');
  django.jQuery('textarea').attr('spellcheck', 'false');
});

(function($) {
  $(document).ready(function() {
    // tour notification btn
    $('body').on('click', '.send_tour_notification', function(e) {
      e.preventDefault();

      var $this = $(this);
      $.post($(this).attr('href'), function(json) {
        if (json.success) {
          $this.after('<span>sent</span>');
          $this.remove();
        } else {
          alert('ERROR: msg not sent');
        }
      }, 'json');
    });
  })
})(jQuery || django.jQuery);
