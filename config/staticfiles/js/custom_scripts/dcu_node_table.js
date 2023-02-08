$(document).ready(function() {
    const table_order_arr = [3, "desc"];
    const table_page_len = 10;

    const table = $('#dcu-node-table').DataTable({
        ajax: {
            type: "GET",
            url: "/load_dcu_node_mappings",
            datatype: "json",
            dataSrc: function (res) {
                let data_list = res.data;
                return data_list;
                },
            data: function (data){
                for (var i = 0, len = data.columns.length; i < len; i++) {
                    if (! data.columns[i].search.value) delete data.columns[i].search;
                    if (data.columns[i].searchable === true) delete data.columns[i].searchable;
                    if (data.columns[i].orderable === true) delete data.columns[i].orderable;
//                    if (data.columns[i].data === data.columns[i].name) delete data.columns[i].name;
                  }
                delete data.search.regex;
                let dateRangeVal = $("#custom_table_filter form input[name=daterange-box]").val();
                let from_time = "";
                let till_time = "";
                if (dateRangeVal) {
                    let dateRangeArr = dateRangeVal.split("  ");
                    from_time = dateRangeArr[0];
                    till_time = dateRangeArr[1];
                }
                data.from_time = from_time.trim();
                data.till_time = till_time.trim();
                },
         },
        processing: true,
        serverSide: true,
        dom: "<'row'<'col-sm-12 col-md-6'l><'#custom_table_filter.col-sm-12 col-md-6'>>" +
                "<'row'<'col-sm-12'tr>>" +
                "<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7'p>>",
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
        order:[table_order_arr],
        columns: [
            {"data": "nodeId", "name": "nodeId", "autoWidth": true},
            {"data": "gwId", "name": "gwId", "autoWidth": true,"orderable": false},
            {"data": "timestamp", "name": "timestamp", "autoWidth": true,"orderable": false},
            {"data": "debugServerTime", "name": "debugServerTime", "autoWidth": true},
            {"data": "last_update_time", "name": "last_update_time", "autoWidth": true,"orderable": false},
            {"data": "sinkId", "name": "sinkId", "autoWidth": true,"orderable": false},
            {"data": "sinkNo", "name": "sinkNo", "autoWidth": true,"orderable": false},
        ],
    });

    const custom_search_form = `<form class="m-auto w-auto float-md-right">
                                    <div class="input-group input-group-sm">
                                        <input type="text" name="search-box" class="form-control bg-light border-1 small" autocomplete="off" placeholder="Search by node or gwId">
                                        <input type="text" autocomplete="off" name="daterange-box" size="25" class="form-control bg-light border-1 small" placeholder="Select Date range">
                                        <div class="input-group-append">
                                            <button class="btn btn-primary" type="submit">
                                                <i class="fas fa-search fa-sm"></i>
                                            </button>
                                        </div>
                                    </div>
                               </form>`;

    const custom_search_form_element = $("#custom_table_filter");
    custom_search_form_element.append(custom_search_form);

    const daterange_element = $("form input[name=daterange-box]", custom_search_form_element);
    const search_element = $("form input[name=search-box]", custom_search_form_element);

//    daterange_element.tooltip({ title: "Select by DebugServerTime", delay: 200 });
//    search_element.tooltip({ title: "Search by GatewayId ", delay: 200 });

    $("form", custom_search_form_element).on("submit", function (e) {
        const search = search_element.val().trim();
        table.search(search).draw();
        e.preventDefault();
    });

    daterange_element.daterangepicker({
        autoUpdateInput: false,
        timePicker: true,
        timePicker24Hour: true,
        timePickerSeconds: true,
        opens: 'center',
        locale: {
            cancelLabel: 'Clear',
            format: "YYYY-MM-DD HH:mm:ss"
        },
        showDropdowns: true
    });

    daterange_element.on('apply.daterangepicker', function (ev, picker) {
        $(this).val(picker.startDate.format('YYYY-MM-DD HH:mm:ss') + '  ' + picker.endDate.format('YYYY-MM-DD HH:mm:ss'));
    });

    daterange_element.on('cancel.daterangepicker', function (ev, picker) {
        $(this).val('');
    });

    // Refresh every 5 min
    setInterval(function () {
        daterange_element.val('');
        search_element.val('');
        table.order(table_order_arr).page.len(table_page_len).draw();
    }, 300000);
});
