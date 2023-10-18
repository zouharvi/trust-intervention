import { DEVMODE } from './globals'
import { MOCKMODE } from './main'

let SERVER_LOG_ROOT = DEVMODE ? "http://127.0.0.1:5000/" : "https://zouharvi.pythonanywhere.com/"

export async function load_data(): Promise<any> {
    // include timestamp so that things don't get cached
    let result = await $.getJSON(
        `baked_queues/${globalThis.uid}.json?t=${Date.now()}`,
    )
    return result
}
export async function log_data(data): Promise<any> {
    if (MOCKMODE) {
        console.log("logged (mock)", data)
        return
    }
    
    data["url_data"] = globalThis.url_data
    console.log("logged", data)

    try {
        let result = await $.ajax(
            SERVER_LOG_ROOT + "log",
            {
                data: JSON.stringify({
                    project: "trust-intervention",
                    uid: globalThis.uid,
                    payload: JSON.stringify(data),
                }),
                type: 'POST',
                contentType: 'application/json',
            }
        )
        return result
    } catch (e) {
        console.log(e)
    }
}