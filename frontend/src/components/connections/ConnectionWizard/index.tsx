import type { ConnectionWizardStep as WizardStep } from '../../../hooks/useConnectionWizard';
import Section from '../../Section';
import ConnectionStep from '../ConnectionStep';

export default function ConnectionWizard({ steps }: { steps: WizardStep[] }) {
  return (
    <Section title="Wizard de Conexão">
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4 2xl:grid-cols-7">
        {steps.map((step) => <ConnectionStep key={step.id} step={step} />)}
      </div>
    </Section>
  );
}
