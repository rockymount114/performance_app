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
                let focusAreasHtml = "";
                let measuresHtml = "";

                const precheckedObjectives = JSON.parse(data.prechecked_objectives_json);
                const precheckedMeasures = JSON.parse(data.prechecked_measures_json);
                const precheckedFocusAreas = JSON.parse(data.prechecked_focus_areas_json);

                data.objectives.forEach(function (objective) {
                    objectivesHtml += getObjectiveRowHtml(objective, precheckedObjectives);
                });

                data.focus_areas.forEach(function (focusArea) {
                    focusAreasHtml += getFocusAreaRowHtml(focusArea, precheckedFocusAreas);
                });

                data.measures.forEach(function (measure) {
                    measuresHtml += getMeasureRowHtml(measure, precheckedMeasures);
                });

                $("#objectivesId").html(objectivesHtml);
                $("#focusAreasId").html(focusAreasHtml);
                $("#measuresId").html(measuresHtml);
            }
        });
    }

    function getObjectiveRowHtml(objective, precheckedObjectives) {
        return `
            <tr>
                <td class="title_column text-center">${objective.fiscal_year__name}</td>
                <td class="title_column" title="${formatDateTime(objective.created_at)}">${formatDateTime(objective.created_at)}</td>
                <td class="title_column">${objective.created_by}</td>
                <td class="title_column text-center">${objective.department__name}</td>
                <td class="title_column" title="${objective.name}"><a href="/view-objective-info/${objective.id}/" class="text-primary">${objective.name}</a></td>
                <td class="text-center">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" value="${objective.id}" name="objective_boxes" ${precheckedObjectives.includes(objective.id) ? 'checked' : ''}>
                    </div>
                </td>
            </tr>
        `;
    }

    function getFocusAreaRowHtml(focusArea, precheckedFocusAreas) {
        return `
            <tr>
                <td class="title_column text-center">${focusArea.fiscal_year__name}</td>
                <td class="title_column" title="${formatDateTime(focusArea.created_at)}">${formatDateTime(focusArea.created_at)}</td>
                <td class="title_column">${focusArea.created_by}</td>
                <td class="title_column text-center">${focusArea.department__name}</td>
                <td class="title_column" title="${focusArea.name}"><a href="/view-focus-area-info/${focusArea.id}/" class="text-primary">${focusArea.name}</a></td>
                <td class="text-center">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" value="${focusArea.id}" name="focus_area_boxes" ${precheckedFocusAreas.includes(focusArea.id) ? 'checked' : ''}>
                    </div>
                </td>
            </tr>
        `;
    }

    function getMeasureRowHtml(measure, precheckedMeasures) {
        return `
            <tr>
                <td class="title_column text-center">${measure.fiscal_year__name}</td>
                <td class="title_column" title="${formatDateTime(measure.created_at)}">${formatDateTime(measure.created_at)}</td>
                <td class="title_column">${measure.created_by}</td>
                <td class="title_column text-center">${measure.department__name}</td>
                <td class="title_column">${measure.objective__name}</td>
                <td class="title_column" title="${measure.title}"><a href="/view-measure-info/${measure.id}/" class="text-primary">${measure.title}</a></td>
                <td class="text-center">
                    <div class="form-check">
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