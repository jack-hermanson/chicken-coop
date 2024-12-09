document.addEventListener("submit", function(event) {
   const form = event.target.closest(".shift-completion-form");
   if (!form || form.getAttribute("data-time-of-day") === "1") return; // Only evening shifts.

   const eggsInput = form.querySelector("input[name='eggs']");
   if (eggsInput && Number(eggsInput.value) > 4) {
       const confirmed = confirm(`Are you sure you want to take ${eggsInput.value} eggs instead of only taking 4 so the morning shift can have some eggs too?`);
       if (!confirmed) {
           event.preventDefault();
       }
   }
});