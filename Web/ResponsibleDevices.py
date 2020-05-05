

def responsible_devices() -> str:
    js = """<script>
    $( document ).ready(function() {
        var width = parseInt($(window).width()) - 40;
        console.log( "ready!" );
        $('.EmbeddedTweet').css('max-width', width.toString());
    });
    </script>
    """
    return js
