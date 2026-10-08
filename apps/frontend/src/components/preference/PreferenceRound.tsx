import {PreferenceCard} from "./PreferenceCard";
export function PreferenceRound({ids}:{ids:string[]}){return <section>{ids.map(id=><PreferenceCard key={id} id={id}/>)}</section>}
