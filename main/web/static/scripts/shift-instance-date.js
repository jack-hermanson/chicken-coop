/**
 * JavaScript's getElementById needs the shift_instance_id to toggle the correct element.
 * This function generates that string.
 * @param {number} shiftInstanceId The shift_instance_id from the database
 * @returns {string} The ID of the element we are looking for
 */
function generateShiftInstanceFormContainerId(shiftInstanceId) {
    return `shift-instance-form-container-${shiftInstanceId}`;
}

/**
 * Function called when user clicks on the completed date so that the form is shown and can be submitted.
 * In other words, the user will click something on the shift instance. When they click it, this function needs
 * to be able to tell that it was clicked and do something about it.
 * @param shiftInstanceId The shift_instance_id from the database
 */
function toggleShiftInstanceForm(shiftInstanceId) {
    const element = document.getElementById(generateShiftInstanceFormContainerId(shiftInstanceId));
    element.classList.toggle("d-none");
}