$(function () {
    $('#container').highcharts({
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: 1,//null,
            plotShadow: false
        },
        title: {
            text: 'Master Database'
        },
        tooltip: {
          pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
        },
        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                dataLabels: {
                    enabled: true,
                    format: '<b>{point.name}</b>: {point.percentage:.1f} %',
                    style: {
                        color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
                    }
                }
            }
        },
        series: [{
            type: 'pie',
            name: 'Freight Content',
            data: [
                ['Payment Processed',  45.0],
                ['Released for Payment',       26.8],
                {
                    name: 'Pending Evaluation',
                    y: 12.8,
                    sliced: true,
                    selected: true
                },
                ['Accepted for Payment',    8.5],
                ['Under Dispute',     6.2],
                ['Dispute Accepted',   0.7]
            ]
        }]
    });
});