(function ($) {
  $(function () {
    function buildTable(data) {
      var header = $(
        `<thead>
          <tr>
            <th>ID</th>
            <th>R</th>
            <th>G</th>
            <th>B</th>
          </tr>
        </thead>`
      );
      var body = $("<tbody></tbody>");
      $("#tbl").empty().append(header, body);

      var content = data.map((v, i) => {
        var color = v.average_color_rgb;
        var r = (color.top[0] + color.center[0] + color.bottom[0])/3;
        var g = (color.top[1] + color.center[1] + color.bottom[1])/3;
        var b = (color.top[2] + color.center[2] + color.bottom[2])/3;
        return $(
          `<tr>
            <td>${v.id}</td>
            <td>${r.toFixed(2)}</td>
            <td>${g.toFixed(2)}</td>
            <td>${b.toFixed(2)}</td>
          </tr>`
        );
      });
      body.append(content);

    }
    function postSuccess(data) {
      $("#original-image").html(`<img src="img/input.jpg?${Date.now()}" />`)
      $("#processed-image").html(`<img src="img/output.jpg?${Date.now()}" />`)
      buildTable(data);
    }
    $("#file-input").change(function (e) {
      data = new FormData()
      data.append("file", this.files[0])
      $.ajax({
        type: "POST",
        url: "/process",
        data: data,
        contentType: false,
        processData: false,
        success: postSuccess,
        error: function () { alert("error") }
      })
    });


    $("#open-button, #original-image").click(function () {
      $('#file-input').trigger('click');
    })

    function refresh() {
      $.ajax({
        type: "POST",
        url: "/refresh",
        success: function (data) { postSuccess(data); console.log("success refresh") },
        error: function () { console.log("failed refresh") }
      })
    }


    function updateConfig(data) {
      $.ajax({
        type: "POST",
        url: "/config",
        data: JSON.stringify(data),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function () { refresh(); console.log("success update") },
        error: function () { console.log("failed update") }
      })
    }
    function initSliders() {

      var sliderArea = document.getElementById("range-area")
      noUiSlider.create(sliderArea, {
        start: [25000, 35000],
        connect: true,
        tooltips: [wNumb({ decimals: 0 }), wNumb({ decimals: 0 })],
        step: 1,
        range: {
          'min': 10000,
          'max': 60000
        }
      });

      var sliderThreshold = document.getElementById("range-threshold")
      noUiSlider.create(sliderThreshold, {
        start: 151,
        tooltips: [wNumb({ decimals: 0 })],
        step: 1,
        range: {
          'min': 0,
          'max': 255
        }
      });

      var sliderRatio = document.getElementById("range-ratio")
      noUiSlider.create(sliderRatio, {
        start: 15,
        tooltips: [wNumb({ decimals: 0 })],
        range: {
          'min': 0,
          'max': 40
        }
      });

      _data = null;
      $.ajax({
        type: "GET",
        url: "/config",
        success: function (data) {
          _data = data;
          sliderRatio.noUiSlider.set(data.minimum_ratio);
          sliderRatio.noUiSlider.on("end", function () {
            _data.minimum_ratio = this.get()
            updateConfig(_data);
          })

          min_area = data.min_area;
          max_area = data.max_area;
          sliderArea.noUiSlider.set([min_area, max_area]);
          sliderArea.noUiSlider.on("end", function () {
            area = this.get();
            _data.min_area = area[0];
            _data.max_area = area[1];
            updateConfig(_data);
          })
          sliderThreshold.noUiSlider.set(data.threshold);
          sliderThreshold.noUiSlider.on("end", function () {
            _data.threshold = this.get()
            updateConfig(_data);
          })
        },
        error: function () { alert("Error getting parameters") }
      })
    }
    initSliders();

  }); // end of document ready

})(jQuery); // end of jQuery name space