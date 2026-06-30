import { useState } from "react";
import { Scale, MapPin, MapPinned, Calendar, Users, Wallet, Loader2, Trophy } from "lucide-react";
import { compareDestinations } from "../api/client";
import "./ComparePage.css";

function ComparePage() {
  const [form, setForm] = useState({
    source: "",
    destination_1: "",
    destination_2: "",
    start_date: "",
    end_date: "",
    travelers: 1,
    budget: "moderate",
    preferences: "",
  });
  
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleCompare = async (e) => {
    e.preventDefault();
    if (!form.destination_1 || !form.destination_2 || !form.start_date || !form.end_date) {
      setError("Please fill in all required fields.");
      return;
    }
    setError(null);
    setLoading(true);
    setResult(null);
    try {
      const data = await compareDestinations(form);
      setResult(data);
    } catch (err) {
      setError("Failed to compare destinations. Please try again.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="compare-page">
      <div className="compare-header">
        <Scale size={28} className="compare-icon" />
        <h2>Compare Destinations</h2>
        <p>Deciding between two places? Let our data-driven AI help you choose.</p>
      </div>

      <form className="compare-form" onSubmit={handleCompare}>
        <div className="form-row">
          <div className="form-group">
            <label><MapPin size={16} /> Source (Optional)</label>
            <input type="text" name="source" value={form.source} onChange={handleChange} placeholder="e.g. New York" />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label><MapPinned size={16} /> Destination 1</label>
            <input type="text" name="destination_1" value={form.destination_1} onChange={handleChange} placeholder="e.g. Paris" required />
          </div>
          <div className="form-group">
            <label><MapPinned size={16} /> Destination 2</label>
            <input type="text" name="destination_2" value={form.destination_2} onChange={handleChange} placeholder="e.g. London" required />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label><Calendar size={16} /> Start Date</label>
            <input type="date" name="start_date" value={form.start_date} onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label><Calendar size={16} /> End Date</label>
            <input type="date" name="end_date" value={form.end_date} onChange={handleChange} required />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label><Users size={16} /> Travelers</label>
            <input type="number" name="travelers" min="1" max="20" value={form.travelers} onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label><Wallet size={16} /> Budget</label>
            <select name="budget" value={form.budget} onChange={handleChange}>
              <option value="budget">Budget / Backpacker</option>
              <option value="moderate">Moderate / Standard</option>
              <option value="luxury">Luxury / Premium</option>
            </select>
          </div>
        </div>

        <div className="form-row">
          <div className="form-group full-width">
            <label>Specific Preferences (Optional)</label>
            <input type="text" name="preferences" value={form.preferences} onChange={handleChange} placeholder="e.g. beaches, hiking, nightlife, vegan food" />
          </div>
        </div>

        {error && <div className="error-message">{error}</div>}

        <button type="submit" className="compare-submit" disabled={loading}>
          {loading ? (
            <>
              <Loader2 className="spinner" size={18} />
              Analyzing Data (This may take ~15s)...
            </>
          ) : (
            "Compare Now"
          )}
        </button>
      </form>

      {result && (
        <div className="compare-result">
          <div className="winner-card">
            <Trophy size={32} className="trophy-icon" />
            <h3>Winner: {result.winner}</h3>
            <p>{result.summary}</p>
          </div>

          <div className="comparison-points">
            {result.comparison_points?.map((point, index) => (
              <div key={index} className="comparison-point-card">
                <h4>{point.category}</h4>
                <div className="point-split">
                  <div className="dest-box">
                    <h5>{form.destination_1}</h5>
                    <p>{point.dest1_info}</p>
                  </div>
                  <div className="dest-box">
                    <h5>{form.destination_2}</h5>
                    <p>{point.dest2_info}</p>
                  </div>
                </div>
                <div className="point-verdict">
                  <strong>Verdict:</strong> {point.verdict}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default ComparePage;
