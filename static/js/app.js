import { showToast } from './modules/toast.js';
import { fetchWorkoutPlan, handleRoutineSelection, updateExerciseDetails, updateExerciseForm, handleAddExercise } from './modules/workout-plan.js';
import { initializeWorkoutLog, deleteWorkoutLog, updateScoredValue, handleDateChange } from './modules/workout-log.js';
import { initializeFilters, initializeAdvancedFilters, initializeSearchFilter, initializeFilterKeyboardEvents } from './modules/filters.js';
import { addExercise, removeExercise } from './modules/exercises.js';
import { initializeUIHandlers, initializeFormHandlers, initializeTooltips, initializeDropdowns, handleTableSort } from './modules/ui-handlers.js';
import { exportToExcel, exportToWorkoutLog, exportSummary } from './modules/exports.js';
import { initializeWorkoutPlanHandlers, updateWorkoutPlanUI } from './modules/workout-plan.js';
import { initializeWorkoutLogFilters } from './modules/workout-log.js';
import { initializeDataTables, initializeCharts } from './modules/ui-handlers.js';
import { 
    fetchWeeklySummary,
    fetchSessionSummary 
} from './modules/summary.js';
import { 
    updateProgressionDate,
    updateProgressionStatus 
} from './modules/workout-log.js';
import { validateScoredValue } from './modules/workout-log.js';
import { 
    checkProgressionStatus,
    initializeProgressionChecks 
} from './modules/workout-log.js';
import { initializeNavHighlighting } from './modules/navbar.js';

// Make certain functions globally available
window.addExercise = addExercise;
window.removeExercise = removeExercise;
window.exportToExcel = exportToExcel;
window.exportToWorkoutLog = exportToWorkoutLog;
window.exportSummary = exportSummary;
window.deleteWorkoutLog = deleteWorkoutLog;
window.updateExerciseDetails = updateExerciseDetails;
window.updateExerciseForm = updateExerciseForm;
window.updateProgressionDate = updateProgressionDate;
window.updateProgressionStatus = updateProgressionStatus;
window.validateScoredValue = validateScoredValue;
window.checkProgressionStatus = checkProgressionStatus;
window.handleAddExercise = handleAddExercise;
window.updateScoredValue = updateScoredValue;
window.handleDateChange = handleDateChange;

document.addEventListener("DOMContentLoaded", () => {
    const currentPath = window.location.pathname;

    // Initialize common UI elements
    initializeUIHandlers();
    initializeFormHandlers();
    initializeTooltips();
    initializeDropdowns();
    handleTableSort();

    // Initialize navbar highlighting
    initializeNavHighlighting();

    // Page-specific initializations
    switch (currentPath) {
        case "/workout_plan":
            initializeFilters();
            initializeFilterKeyboardEvents();
            initializeAdvancedFilters();
            initializeSearchFilter();
            handleRoutineSelection();
            initializeWorkoutPlanHandlers();
            fetchWorkoutPlan();
            break;

        case "/workout_log":
            initializeWorkoutLog();
            break;

        case "/weekly_summary":
            initializeCharts();
            fetchWeeklySummary();
            break;

        case "/session_summary":
            initializeCharts();
            fetchSessionSummary();
            break;

        default:
            // Handle other pages or show error for unknown routes
            console.log(`No specific initialization for path: ${currentPath}`);
    }
});

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    const currentPath = window.location.pathname;
    console.log('DOM loaded, initializing modules. Current path:', currentPath);
    
    // Check if we're on the workout log page
    if (currentPath === '/workout_log') {
        console.log('Workout log page detected, initializing...');
        initializeWorkoutLog();
    }
});
