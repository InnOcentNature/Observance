$(document).ready(function() {
    const csrftoken = getCookie('csrftoken');
    $('#dcu-table').DataTable({
        ajax: {
            type: "POST",
            url: "/data/load_dcu_data/",
            headers: {'X-CSRFToken': csrftoken},
            data: {
                "value": "Nature",
            },
        },
        processing: true,
        serverSide: true,
        lengthMenu: [[10, 25, 50, 100, 5000], [10, 25, 50, 100, "All"]],
        pageLength: 10,
        language: {
        processing: 'Processing...',
        zeroRecords: "data not found",
        infoEmpty: "No records available"
        },
        deferRender: true,
        searchDelay: 1000,
        scrollX: true,
        scrollCollapse: true,
        pagingType: "full_numbers",
        filter: true,
        orderMulti: false,
        columns: [
            {"data": "gwId", "name": "gwId", "autoWidth": true},
            {"data": "epochTime", "name": "epochTime", "autoWidth": true},
            {"data": "debugServerTime", "name": "debugServerTime", "autoWidth": true},
        ],
    });
});


//  Getting CSRF token for POST request
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}