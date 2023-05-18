import { DEVMODE } from "./globals"
export var UID: string
import { load_data, log_data } from './connector'
import { paramsToObject } from "./utils"

var data: any[] = []
let question_i = -1
let question = null
let user_decision: null | boolean = null
let balance = 0
let bet_val: number
let time_question_start: number
let time_bet_start: number
let time_showed_results_start: number
let instruction_i: number = 0
let count_exited_page: number = 0

function next_instructions(increment: number) {
    instruction_i += increment

    if (instruction_i == 0) {
        $("#button_instructions_prev").attr("disabled", "true")
    } else {
        $("#button_instructions_prev").removeAttr("disabled")
    }
    if (instruction_i >= 5) {
        $("#instructions_and_decorations").show()
        $("#button_instructions_next").val("Start study")
    } else {
        $("#instructions_and_decorations").hide()
        $("#button_instructions_next").val("Next")
    }
    if (instruction_i == 6) {
        $("#main_box_instructions").hide()
        $("#main_box_experiment").show()
        next_question()
    }

    $("#main_box_instructions").children(":not(input)").each((_, el) => {
        $(el).hide()
    })
    $(`#instructions_${instruction_i}`).show()
}
$("#button_instructions_next").on("click", () => next_instructions(+1))
$("#button_instructions_prev").on("click", () => next_instructions(-1))

$("#button_next").on("click", () => {
    if (question_i != -1) {
        let logged_data = {
            "question_i": question_i,
            "user_balance": balance,
            "user_bet_val": bet_val,
            "user_decision": user_decision,
        }

        logged_data['times'] = {
            "decision": time_bet_start - time_question_start,
            "bet": time_showed_results_start - time_bet_start,
            "next": Date.now() - time_showed_results_start
        }
        logged_data['question'] = question
        logged_data['count_exited_page'] = count_exited_page
        log_data(logged_data)
        count_exited_page = 0
    }
    next_question()
});

$('#range_val').on('input change', function () {
    bet_val = ($(this).val()! as number) / 5 * 0.1
    $("#range_text").text(`If you are right, you get $${bet_val.toFixed(2)}. If you are wrong, you lose $${bet_val.toFixed(2)}.`)
    $("#button_place_bet").show()
});

function flip_user_decision(correct) {
    time_bet_start = Date.now()
    user_decision = correct
    if (correct) {
        $("#button_decision_correct").attr("activedecision", "true")
        $("#button_decision_incorrect").removeAttr("activedecision")
    } else {
        $("#button_decision_correct").removeAttr("activedecision")
        $("#button_decision_incorrect").attr("activedecision", "true")
    }
    $("#how_confident_div").show()
}

$("#button_decision_correct").on("click", () => flip_user_decision(true))
$("#button_decision_incorrect").on("click", () => flip_user_decision(false))

function show_result() {
    time_showed_results_start = Date.now()

    let message = "You guessed that the system was "
    let success: boolean
    if (user_decision) {
        message += "<span class='color_correct'>correct</span> "
        if (question!["ai_is_correct"]) {
            message += "and the system was <span class='color_correct'>correct</span>."
            success = true
        } else {
            message += "but the system was <span class='color_incorrect'>not correct</span>."
            success = false
        }
    } else {
        message += "<span class='color_incorrect'>incorrect</span> "
        if (!question!["ai_is_correct"]) {
            message += "and the system was <span class='color_incorrect'>not correct</span>."
            success = true
        } else {
            message += "but the system was <span class='color_correct'>correct</span>."
            success = false
        }
    }
    message += "<br>"
    if (success) {
        message += `You gain $${bet_val}.`
        balance += bet_val
    } else {
        message += `You lose $${bet_val}.`
        balance -= bet_val
        balance = Math.max(0, balance)
    }
    $("#balance").text(`Balance: $${balance.toFixed(2)} + $0.5`)
    $("#result_span").html(message)
    $("#button_next").show()
    $("#result_span").show()
    $("#button_place_bet").hide()

    $('#range_val').attr("disabled", "true")
    $("#button_decision_incorrect").attr("disabled", "true")
    $("#button_decision_correct").attr("disabled", "true")
}

$("#button_place_bet").on("click", show_result)

function next_question() {
    // restore previous state of UI
    $("#button_decision_incorrect").removeAttr("activedecision")
    $("#button_decision_correct").removeAttr("activedecision")
    $("#button_decision_incorrect").removeAttr("disabled")
    $("#button_decision_correct").removeAttr("disabled")
    $('#range_val').removeAttr("disabled")
    $("#how_confident_div").hide()
    $("#button_place_bet").hide()
    $("#button_next").hide()
    $("#result_span").hide()
    $("#range_text").text("-")
    $("#range_val").val(3)

    question_i += 1
    if (question_i >= data.length) {
        $("#main_box_experiment").hide()
        $("#main_box_end").show()
        return
    }
    question = data[question_i]

    $("#question_span").text(question!["question"])
    $("#answer_span").text(question!["answer"])
    $("#confidence_span").text(question!["ai_confidence"])

    time_question_start = Date.now()
    $("#progress").text(`Progress: ${question_i + 1} / ${data.length}`)
}

// get user id and load queue
// try to see if start override was passed
const urlParams = new URLSearchParams(window.location.search);
const startOverride = urlParams.get('start');
const UIDFromURL = urlParams.get("uid")
globalThis.url_data = paramsToObject(urlParams.entries())

if (UIDFromURL != null) {
    globalThis.uid = UIDFromURL as string
    if (globalThis.uid == "prolific_random") {
        let queue_id = `${Math.floor(Math.random() * 50)}`.padStart(3, "0")
        globalThis.uid = `${urlParams.get("prolific_queue_name")}_${queue_id}`
    }
} else if (DEVMODE) {
    globalThis.uid = "demo"
} else {
    let UID_maybe: any = null
    while (UID_maybe == null) {
        UID_maybe = prompt("Enter your user id. Please get in touch if you were not assigned an id but wish to participate in this experiment.")
    }
    globalThis.uid = UID_maybe!
}

load_data().catch((_error) => {
    alert("Invalid user id.")
    window.location.reload()
}
).then((new_data) => {
    data = new_data
    if (startOverride != null) {
        question_i = parseInt(startOverride) - 1
        console.log("Starting from", question_i)
    }
    // next_question()
    next_instructions(0)
    $("#main_box_instructions").show()
    $("#instructions_and_decorations").hide()
})

console.log("Starting session with UID:", globalThis.uid!)

let alert_active = false
document.onvisibilitychange = () => {
    if (!alert_active) {
        count_exited_page += 1
        alert_active = true
        alert("Please don't leave the page. If you do so again, we may restrict paying you.")
        alert_active = false
    }
}