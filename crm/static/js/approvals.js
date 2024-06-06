// approvals.js
$(document).ready(function() {

    // Use event delegation to handle checkbox changes
    $(document).on('change', 'input[type="checkbox"]', function() {
        var itemType = $(this).attr('name').split('_')[0];
        var itemId = $(this).val();
        var isChecked = $(this).is(':checked');

        $.ajax({
            url: "/update-session/",
            type: 'POST',
            data: {
                'item_type': itemType,
                'item_id': itemId,
                'is_checked': isChecked,
                'csrfmiddlewaretoken': getCookie('csrftoken')
            },
            success: function(data) {
                console.log(data.message);
            }
        });
    });

    $("#resetFiltersBtn").click(function () {
        $("#id_departments").val("").change();
        $("#id_fiscal_year").val("").change();
        updateTableData();
    });

    $("#id_departments").change(function () {
        updateTableData();
    });

    $("#id_fiscal_year").change(function () {
        updateTableData();
    });

    function formatDateTime(dateTimeString) {
        const options = { year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: 'numeric' };
        return new Date(dateTimeString).toLocaleDateString(undefined, options);
    }

    function formatDateTime2(dateTimeString) {
        const options = { year: '2-digit', month: '2-digit', day: '2-digit' };
        return new Date(dateTimeString).toLocaleString(undefined, options);
    }

    // Fetch initial table data on page load
    updateTableData();

    function updateTableData() {
        const url = $("#approvalsForm").attr("data-approvals-filter-url");
        const departmentId = $("#id_departments").val();
        const fiscalYearId = $("#id_fiscal_year").val();

        $.ajax({
            url: url,
            type: 'GET',
            data: {
                'department_id': departmentId,
                'fiscal_year_id': fiscalYearId
            },
            success: function (data) {
                console.log(data);
                let objectivesHtml = "";
                let measuresHtml = "";

                const precheckedObjectives = JSON.parse(data.prechecked_objectives_json);
                const precheckedMeasures = JSON.parse(data.prechecked_measures_json);
             

                data.objectives.forEach(function (objective) {
                    objectivesHtml += getObjectiveRowHtml(objective, precheckedObjectives);
                });


                data.measures.forEach(function (measure) {
                    measuresHtml += getMeasureRowHtml(measure, precheckedMeasures);
                });


                $("#objectivesId").html(objectivesHtml);
                $("#measuresId").html(measuresHtml);

                // Initialize tooltips on the newly added elements
                $('[data-toggle="tooltip"]').tooltip();
            }
        });
    }

    function getObjectiveRowHtml(objective, precheckedObjectives) {
        return `
            <tr>
                <td class="title_column text-center">${objective.fiscal_year__name}</td>
                <td class="text-center" data-toggle="tooltip" title="${formatDateTime(objective.created_at)}">${formatDateTime2(objective.created_at)}</td>
                <td class="title_column">${objective.created_by}</td>
                <td class="title_column text-center">${objective.department__name}</td>
                <td class="title_column"  data-toggle="tooltip" title="${objective.name}"><a href="/view-objective-info/${objective.id}/" class="text-primary">${objective.name}</a></td>
                <td class="text-center">
                    <div class="form-check d-flex justify-content-center">
                        <input class="form-check-input" type="checkbox" value="${objective.id}" name="objective_boxes" ${precheckedObjectives.includes(objective.id) ? 'checked' : ''}>
                    </div>
                </td>
            </tr>
        `;
    }



    function getMeasureRowHtml(measure, precheckedMeasures) {
        return `
            <tr>
                <td class="title_column text-center">${measure.fiscal_year__name}</td>
                <td class="title_column text-center" data-toggle="tooltip" title="${formatDateTime(measure.created_at)}">${formatDateTime2(measure.created_at)}</td>
                <td class="title_column">${measure.created_by}</td>
                <td class="title_column text-center">${measure.department__name}</td>
                <td  data-toggle="tooltip" title="${measure.objective__name}" >${measure.objective__name}</td>
                <td  data-toggle="tooltip" title="${measure.title}"><a href="/view-measure-info/${measure.id}/" class="text-primary">${measure.title}</a></td>
                <td class="text-center">
                    <div class="form-check d-flex justify-content-center">
                        <input class="form-check-input" type="checkbox" value="${measure.id}" name="measure_boxes" ${precheckedMeasures.includes(measure.id) ? 'checked' : ''}>
                    </div>
                </td>
            </tr>
        `;
    }
    

});




// CSRF token retrieval function
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

