// ==========================================
// 1. HOME PAGE LOGIC (Only runs on Home)
// ==========================================
const tableBody = document.getElementById('tableBody');

if (tableBody) { // Checks if we are on the Home Page
    const chores = JSON.parse(localStorage.getItem('myChores') || "[]");

    // Build the table
    chores.forEach((item) => {
        const row = document.createElement('tr');
        row.innerHTML = `<td><input type="checkbox" class="chore-check"></td>
                        <td>${item.task}</td>
                        <td>${item.points}</td>
                        <td>${item.person}</td>`; // This will now hold the ML's choice!
        tableBody.appendChild(row); 
    });

    // Clear completed
    document.getElementById('deleteCheckedBtn').onclick = function() {
        const checkboxes = document.querySelectorAll('.chore-check');
        const updatedChores = chores.filter((item, index) => {
            return !checkboxes[index].checked;
        });
        localStorage.setItem('myChores', JSON.stringify(updatedChores));
        location.reload();
    };

    // Empty everything
    document.getElementById('clearBtn').onclick = function() {
        if (confirm("Are you sure you want to delete ALL chores?")) {
            localStorage.removeItem('myChores'); 
            location.reload(); 
        }
    };
}


// ==========================================
// 2. ADD CHORE PAGE LOGIC (Only runs on Add page)
// ==========================================
const saveBtn = document.getElementById('saveBtn'); // Make sure your button has id="saveBtn"

if (saveBtn) { // Checks if we are on the Add Chore Page
    saveBtn.onclick = async function() {
        const choreValue = document.getElementById('choreInput').value;
        const pointsValue = document.getElementById('pointsInput').value;

        if (choreValue.trim() === "") {
            alert("Please enter a chore name!");
            return;
        }

        // Change button text so the user knows the AI is thinking!
        saveBtn.innerText = "ML is Assigning..."; 
        saveBtn.disabled = true; 

        try {
            // 1. Ask the ML model who should do it
            const assignedPerson = await getChoreAssignment(pointsValue);

            // 2. Get existing chores
            let chores = JSON.parse(localStorage.getItem('myChores') || "[]");

            // 3. Save the new chore WITH the AI's chosen person
            chores.push({ 
                task: choreValue, 
                points: pointsValue,
                person: assignedPerson // <--- Here is the magic!
            });

            localStorage.setItem('myChores', JSON.stringify(chores));

            // 4. Redirect to home page
            window.location.href = "home.html"; 

        } catch (error) {
            alert("Error connecting to the ML model. Is your server running?");
            saveBtn.innerText = "SAVE CHORE";
            saveBtn.disabled = false;
        }
    };
}


// ==========================================
// 3. THE MACHINE LEARNING API CALL
// ==========================================
async function getChoreAssignment(newChorePoints) {
    
    // We get the current list to calculate how many points everyone ALREADY has
    const chores = JSON.parse(localStorage.getItem('myChores') || "[]");
    
    // Helper object to total up the points dynamically
    let currentPoints = { Zain: 0, Jasmine: 0, Justin: 0, Chloe: 0 };
    
    chores.forEach(chore => {
        if (currentPoints[chore.person] !== undefined) {
            // Add the points (converting string to number)
            currentPoints[chore.person] += parseInt(chore.points); 
        }
    });

    // Package the dynamic data for Python model
    const choreData = {
        chore_difficulty: parseInt(newChorePoints),
        zain_pts: currentPoints.Zain,
        jasmine_pts: currentPoints.Jasmine,
        justin_pts: currentPoints.Justin,
        chloe_pts: currentPoints.Chloe
    };

    const response = await fetch('http://127.0.0.1:5000/assign_chore', { 
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(choreData)
    });

    const result = await response.json();

    // If Python sends an error back, stop immediately.
    if (result.error) {
        console.error("Python Server Error:", result.error);
        throw new Error("The AI model had an error. Check the Python terminal!");
    }
    
    console.log("The ML model assigned this to:", result.assigned_to);
    
    return result.assigned_to; // Returns the name back to the Save button
}