

<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<script>
$(document).ready(function() {
    // Handle checkbox change events
    $('.form-check-input').change(function() {
        var pinId = $(this).data('pin-id');
        var isChecked = $(this).is(':checked');
        var url = isChecked ? '{% url "switch_on" %}' : '{% url "switch_off" %}';

        $.ajax({
            url: url,
            type: 'POST',
            data: {
                'pin_id': pinId,
                'csrfmiddlewaretoken': '{{ csrf_token }}'  // CSRF token for POST requests
            },
            success: function(response) {
                // Handle success (if needed)
                console.log('State changed successfully:', response);
            },
            error: function(xhr, errmsg, err) {
                // Handle error (if needed)
                console.log('Error:', errmsg);
            }
        });
    });
});
</script>
