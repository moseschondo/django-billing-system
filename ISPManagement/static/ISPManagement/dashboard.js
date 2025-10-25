function showForm(type) {
    const overlay = document.getElementById('formOverlay');
    const staticForm = document.getElementById('staticForm');
    const pppoeForm = document.getElementById('pppoeForm');

    // Reset
    overlay.classList.remove('d-none');
    staticForm.classList.add('d-none');
    pppoeForm.classList.add('d-none');

    // Show the selected one
    if (type === 'static') {
      staticForm.classList.remove('d-none');
    } else if (type === 'pppoe') {
      pppoeForm.classList.remove('d-none');
    }
  }

  // Hide form overlay after submission
  document.querySelectorAll("#formOverlay form").forEach(form => {
    form.addEventListener("submit", function () {
      setTimeout(() => {
        document.getElementById("formOverlay").classList.add("d-none");
        form.classList.add("d-none");
      }, 300); // adjust delay if needed
    });
  });

var xValues = ["Sunday", "Monady", "Tuesday", "Wednesday", "Thursday","Friday","Saturday"];
var yValues = [1500, 1400, 1600, 1400, 1600,1800,2000];
var barColors = ["red", "green","blue","orange","brown","black","orange"];

new Chart("myChart", {
  type: "bar",
  data: {
    labels: xValues,
    datasets: [{
      backgroundColor: barColors,
      data: yValues
    }]
  },
 options: {
    legend: {display: false},
    title: {
      display: true,
      text: "Weekly income trend"
    }
  }
});



function showForm(type) {
        const overlay = document.getElementById('formOverlay');
        const staticForm = document.getElementById('staticForm');
        const pppoeForm = document.getElementById('pppoeForm');

        // Reset
        overlay.classList.remove('d-none');
        staticForm.classList.add('d-none');
        pppoeForm.classList.add('d-none');

        // Show the selected one
        if (type === 'static') {
          staticForm.classList.remove('d-none');
        } else if (type === 'pppoe') {
          pppoeForm.classList.remove('d-none');
        }
      }

      // Hide form overlay after submission
      document.querySelectorAll("#formOverlay form").forEach(form => {
        form.addEventListener("submit", function () {
          setTimeout(() => {
            document.getElementById("formOverlay").classList.add("d-none");
            form.classList.add("d-none");
          }, 300); // adjust delay if needed
        });
      });

      function myFunction() {
      var x = document.getElementById("myLinks");
      if (x.style.display === "block") {
        x.style.display = "none";
      } else {
        x.style.display = "block";
      }
    }
    var xValues = ["Sunday", "Monady", "Tuesday", "Wednesday", "Thursday","Friday","Saturday"];
    var yValues = [1500, 1400, 1600, 1400, 1600,1800,2000];
    var barColors = ["red", "green","blue","orange","brown","black","orange"];

    new Chart("myChart", {
      type: "bar",
      data: {
        labels: xValues,
        datasets: [{
          backgroundColor: barColors,
          data: yValues
        }]
      },
    options: {
        legend: {display: false},
        title: {
          display: true,
          text: "Weekly income trend"
        }
      }
    });

// static/js/form_validation.js

// function isValidIP(ip) {
//     const ipPattern = /^(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)(\.(?!$)|$){4}$/;
//     return ipPattern.test(ip);
// }

// function isValidCIDR(cidr) {
//     const cidrPattern = /^((25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)(\.|$)){4}\/([0-9]|[1-2][0-9]|3[0-2])$/;
//     return cidrPattern.test(cidr);
// }

// document.addEventListener("DOMContentLoaded", function () {
//     const form = document.getElementById("staticForm");
//     if (!form) return;

//     form.addEventListener("submit", function (e) {
//         const ip = document.getElementById("ip").value;
//         const subnet = document.getElementById("subnet").value;
//         const cidr = document.getElementById("cidr").value;
//         const dns = document.getElementById("dns").value;
//         const errorMsg = document.getElementById("error-msg");
//         errorMsg.innerHTML = "";

//         if (!isValidIP(ip)) {
//             errorMsg.innerHTML = "Invalid IP address.";
//             e.preventDefault();
//             return;
//         }

//         if (!isValidIP(subnet)) {
//             errorMsg.innerHTML = "Invalid subnet mask.";
//             e.preventDefault();
//             return;
//         }

//         if (!isValidCIDR(cidr)) {
//             errorMsg.innerHTML = "Invalid CIDR notation.";
//             e.preventDefault();
//             return;
//         }

//         if (!isValidIP(dns)) {
//             errorMsg.innerHTML = "Invalid DNS address.";
//             e.preventDefault();
//             return;
//         }
//     });
// });
