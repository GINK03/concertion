


def responsible_devices() -> str:
    js = """<script>
    $( document ).ready(function() {
        var width = Math.min(parseInt($(window).width()) - 40, 800);
        console.log( "ready!" );
        $('.EmbeddedTweet').css('max-width', width.toString());
    });
    </script>
    """
    return js
