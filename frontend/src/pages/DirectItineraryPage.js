import {
  CalendarDays,
  FileText,
  Loader2,
  Map,
  Plane,
  Users,
  Wallet,
} from "lucide-react";
import TripResult from "../components/TripResult";
import "./DirectItineraryPage.css";

const emptyItineraryForm = {
  source: "",
  destination: "",
  start_date: "",
  end_date: "",
  travelers: 1,
  budget: "",
  preference_prompt: "",
};

function DirectItineraryPage({
  form,
  setForm,
  loading,
  result,
  onGenerate,
}) {
  function updateForm(field, value) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  function resetForm() {
    setForm(emptyItineraryForm);
  }

  return (
    <section className="form-layout">
      <form className="itinerary-form" onSubmit={onGenerate}>
        <div className="form-header">
          <div>
            <p className="eyebrow">Direct Planner</p>
            <h2>Generate Itinerary From Form</h2>
          </div>
          <button type="button" className="secondary-button" onClick={resetForm}>
            Reset
          </button>
        </div>

        <div className="form-grid">
          <Field label="Source" icon={<Map size={17} />}>
            <input
              required
              value={form.source}
              onChange={(event) => updateForm("source", event.target.value)}
              placeholder="Mumbai"
            />
          </Field>

          <Field label="Destination" icon={<Plane size={17} />}>
            <input
              required
              value={form.destination}
              onChange={(event) => updateForm("destination", event.target.value)}
              placeholder="Goa"
            />
          </Field>

          <Field label="Start Date" icon={<CalendarDays size={17} />}>
            <input
              required
              type="date"
              value={form.start_date}
              onChange={(event) => updateForm("start_date", event.target.value)}
            />
          </Field>

          <Field label="End Date" icon={<CalendarDays size={17} />}>
            <input
              required
              type="date"
              value={form.end_date}
              onChange={(event) => updateForm("end_date", event.target.value)}
            />
          </Field>

          <Field label="No. of Travellers" icon={<Users size={17} />}>
            <input
              required
              min="1"
              type="number"
              value={form.travelers}
              onChange={(event) => updateForm("travelers", event.target.value)}
            />
          </Field>

          <Field label="Budget" icon={<Wallet size={17} />}>
            <input
              required
              value={form.budget}
              onChange={(event) => updateForm("budget", event.target.value)}
              placeholder="INR 50000"
            />
          </Field>
        </div>

        <label className="field field-wide">
          <span>
            <FileText size={17} />
            Preference Prompt
          </span>
          <textarea
            value={form.preference_prompt}
            onChange={(event) => updateForm("preference_prompt", event.target.value)}
            placeholder="Tell us what you want: adventure, beaches, food, relaxed pace, vegetarian food, avoid early mornings..."
            rows={5}
          />
        </label>

        <button className="generate-button" type="submit" disabled={loading || !!result}>
          {loading ? <Loader2 className="spin" size={20} /> : <FileText size={20} />}
          Generate Itinerary
        </button>
      </form>

      <TripResult result={result} />
    </section>
  );
}

function Field({ label, icon, children }) {
  return (
    <label className="field">
      <span>
        {icon}
        {label}
      </span>
      {children}
    </label>
  );
}

export { emptyItineraryForm };
export default DirectItineraryPage;
