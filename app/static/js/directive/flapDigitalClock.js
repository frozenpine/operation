app.directive('digitalClock', function($interval) {
    return {
        restrict: 'AE',
        scope: {
            title: '@',
            theme: '@',
            zoom: '@'
        },
        replace: true,
        template: '<div id=clock class="{{theme}}" style="line-height: normal; height: 100%">' +
            /* '<div class="display">' +
            '<div class="weekdays"></div>' +
            '<div class="ampm"></div>' +
            '<div class="alarm"></div>' + */
            '<div class="digits"></div>' +
            '<div class="bold am-text-right am-text-success">' +
            '<i class="am-icon-heartbeat" style="margin-right: 3px;"></i>' +
            '{{title}}' +
            '</div>' +
            /* '</div>' + */
            '</div>',
        link: function($scope, $element, $attr) {
            var now;
            var second_interval;
            // Cache some selectors
            var clock = $element,
                alarm = clock.find('.alarm'),
                ampm = clock.find('.ampm');

            // Map digits to their names (this will be an array)
            var digit_to_name = 'zero one two three four five six seven eight nine'.split(' ');

            // This object will hold the digit elements
            var digits = {};

            // Positions for the hours, minutes, and seconds
            var positions = [
                'h1', 'h2', ':', 'm1', 'm2', ':', 's1', 's2'
            ];

            // Generate the digits with the needed markup,
            // and add them to the clock

            var digit_holder = clock.find('.digits');
            if ($scope.zoom !== undefined) {
                digit_holder.css('zoom', $scope.zoom);
            }

            var heartbeat = clock.find('.am-icon-heartbeat');

            $.each(positions, function() {
                if (this == ':') {
                    digit_holder.append('<div class="dots">');
                } else {
                    var pos = $('<div>');
                    for (var i = 1; i < 8; i++) {
                        pos.append('<span class="d' + i + '">');
                    }
                    // Set the digits as key:value pairs in the digits object
                    digits[this] = pos;
                    // Add the digit elements to the page
                    digit_holder.append(pos);
                }
            });

            // Add the weekday names
            var weekday_names = 'MON TUE WED THU FRI SAT SUN'.split(' '),
                weekday_holder = clock.find('.weekdays');
            $.each(weekday_names, function() {
                weekday_holder.append('<span>' + this + '</span>');
            });
            var weekdays = clock.find('.weekdays span');

            // Run a timer every second and update the clock
            function update_time() {
                hour_1 = parseInt(now[0]);
                hour_2 = parseInt(now[1]);
                minute_1 = parseInt(now[2]);
                minute_2 = parseInt(now[3]);
                second_1 = parseInt(now[4]);
                second_2 = parseInt(now[5]) + 1;
                if (second_2 >= 10) {
                    second_1 += 1;
                    second_2 = 0;
                }
                if (second_1 >= 6) {
                    minute_2 += 1;
                    second_1 = 0;
                }
                if (minute_2 >= 10) {
                    minute_1 += 1;
                    minute_2 = 0;
                }
                if (minute_1 >= 6) {
                    hour_2 += 1;
                    minute_1 = 0;
                }
                if (hour_1 < 2) {
                    if (hour_2 >= 10) {
                        hour_1 += 1;
                        hour_2 = 0;
                    }
                } else {
                    if (hour_2 >= 4) {
                        hour_1 = 0;
                        hour_2 = 0;
                    }
                }
                now[2] = minute_1.toString();
                now[3] = minute_2.toString();
                now[4] = second_1.toString();
                now[5] = second_2.toString();
                digits.h1.attr('class', digit_to_name[now[0]]);
                digits.h2.attr('class', digit_to_name[now[1]]);
                digits.m1.attr('class', digit_to_name[now[2]]);
                digits.m2.attr('class', digit_to_name[now[3]]);
                digits.s1.attr('class', digit_to_name[now[4]]);
                digits.s2.attr('class', digit_to_name[now[5]]);

                heartbeat.toggleClass('heartbeat');
                setTimeout(function() { heartbeat.toggleClass('heartbeat'); }, 500);

                // The library returns Sunday as the first day of the week.
                // Stupid, I know. Lets shift all the days one position down, 
                // and make Sunday last

                /* var dow = now[6];
                dow--; */

                // Sunday!
                /* if (dow < 0) {
                    // Make it last
                    dow = 6;
                } */

                // Mark the active day of the week
                // weekdays.removeClass('active').eq(dow).addClass('active');

                // Set the am/pm text:
                // ampm.text(now[7] + now[8]);

                // Schedule this function to be run again in 1 sec
                // setTimeout(update_time, 1000);
            }

            $scope.$on('heartbeat', function(event, data) {
                var serverTime = data.split(' ')[1].replace(/:/g, '');
                now = serverTime.split('');
                if (second_interval === undefined) {
                    second_interval = $interval(update_time, 1000);
                } else {
                    $interval.cancel(second_interval);
                    update_time();
                    second_interval = $interval(update_time, 1000);
                }
            });
        }
    };
});