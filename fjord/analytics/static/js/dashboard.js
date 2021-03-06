$(function() {
    // Draw bars in the left column.
    $('ul.bars').each(function() {
        var $ul = $(this);
        var total = $ul.data('total');
        var max_value = 0;
        var $all_li = $ul.children('li');
        var width = $ul.width();
        var name = $ul.attr('name');

        // Find the maximum value, which will have width=100%
        $all_li.each(function() {
            var $li = $(this);
            var value = $li.data('value');
            if (value > max_value) {
                max_value = value;
            }
        });

        $all_li.each(function() {
            var $li = $(this);
            var value = $li.data('value');
            var bar_width = (value / max_value * 100).toString() + '%';
            var percent = (value / total * 100).toFixed(0).toString() + '%';
            var $label = $li.children('label');

            // Draw bars
            $('<span class="bar_bg"/>').css({'width': bar_width}).prependTo($label);
            $('<span class="percent"/>').text(percent).appendTo($label);
            $('<span class="count"/>').text(value).appendTo($label);

            // Click events for faceting
            $li.children('input').bind('click', function() {
                var $input = $(this);
                var params = {};
                if ($input.attr('checked')) {
                    params[name] = $(this).attr('value');
                } else {
                    params[name] = undefined;
                }
                setQuerystring(getQuerystring(), params);
            });
        });
    });

    // Draw histogram in the middle column.
    var $histogram = $('.graph .histogram');
    var data = $histogram.data('histogram');
    colors = {
        'happy': '#72BF3E',
        'sad': '#AA4643'
    };
    for (var i = 0; i < data.length; i++) {
        var label = data[i]['label'].toLowerCase();
        var color = colors[label];
        if (color === undefined) {
            color = '#000000';
        }
        data[i]['color'] = color;
    }
    var options = {
        series: {
            hover: true,
            lines: { show: true, fill: false },
            points: { show: true }
        },
        xaxis: {
            mode: 'time',
            timezone: 'browser',
            timeformat: ('%b %d')
        },
        yaxis: {
            min: 0
        },
        legend: {
            container: $('.graph .legend'),
            noColumns: 2 // number of columns
        }
    };
    var plot = $.plot($histogram, data, options);
});
