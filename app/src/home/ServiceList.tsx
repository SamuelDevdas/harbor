import { useState } from "react";

import { IconRotateCW } from "../Icons";
import { Section } from "../Section";
import { ServiceCard } from "./ServiceCard";
import { useServiceList } from "./useServiceList";
import { useArrayState } from "../useArrayState";
import { LinearLoader } from "../LinearLoading";
import { IconButton } from "../IconButton";
import { ACTION_ICONS, HarborService, HST } from "../serviceMetadata";
import { runHarbor } from "../useHarbor";
import { toasted } from "../utils";

const serviceOrderBy = (a: HarborService, b: HarborService) => {
    if ((a.isRunning || a.isDefault) && !(b.isRunning || b.isDefault)) {
        return -1;
    }
    if (!(a.isRunning || a.isDefault) && (b.isRunning || b.isDefault)) {
        return 1;
    }

    return a.handle.localeCompare(b.handle, undefined, {
        numeric: true,
        sensitivity: "base",
    });
};

export const ServiceList = () => {
    const { services, loading, error, rerun } = useServiceList();
    const { toggle, items } = useArrayState(useState<string[]>([]));
    const [changing, setChanging] = useState(false);

    const handleTagsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, checked } = e.target;
        toggle(name, checked);
    };

    const handleServiceUpdate = () => {
        rerun();
    };

    const filteredServices = services?.filter((service) => {
        if (!items.length) {
            return true;
        }

        return service.tags.some((tag) => {
            return items.includes(tag);
        });
    });

    const orderedServices = filteredServices?.sort(serviceOrderBy);
    const anyRunning = orderedServices?.some((service) => service.isRunning);
    const actionIcon = changing
        ? ACTION_ICONS.loading
        : anyRunning
        ? ACTION_ICONS.down
        : ACTION_ICONS.up;
    const actionTip = anyRunning
        ? "Stop all services"
        : `Start default services`;

    const handleToggle = () => {
        const msg = (str: string) => <span>{str}</span>;

        const action = () => {
            setChanging(true);
            return runHarbor([
                anyRunning ? "down" : "up",
            ]);
        };
        const ok = anyRunning ? msg("All services stopped") : msg("Started default services");
        const error = anyRunning
            ? msg("Failed to stop all services")
            : msg("Failed to start default services");

        toasted({
            action,
            ok,
            error,
            finally() {
                setChanging(false);
                handleServiceUpdate();
            },
        });
    };

    return (
        <Section
            header={
                <div className="flex flex-wrap gap-4 items-center mb-4">
                    <span>Services</span>
                    <div className="join flex-wrap">
                        {Object.values(HST).map((tag) => {
                            return (
                                <input
                                    key={tag}
                                    onChange={handleTagsChange}
                                    className="join-item btn btn-sm"
                                    type="checkbox"
                                    name={tag}
                                    aria-label={tag}
                                />
                            );
                        })}
                    </div>

                    <span
                        className="tooltip tooltip-bottom"
                        data-tip={actionTip}
                    >
                        <IconButton
                            icon={actionIcon}
                            onClick={handleToggle}
                            disabled={changing}
                        />
                    </span>

                    <span className="tooltip tooltip-bottom" data-tip="Refresh">
                        <IconButton icon={<IconRotateCW />} onClick={rerun} />
                    </span>
                </div>
            }
            children={
                <>
                    <LinearLoader loading={loading} />
                    {error && <div className="my-2">{error.message}</div>}
                    {services && (
                        <ul className="flex gap-4 flex-wrap">
                            {orderedServices.map((service) => {
                                return (
                                    <li
                                        key={service.handle}
                                        className="m-0 p-0"
                                    >
                                        <ServiceCard
                                            service={service}
                                            onUpdate={handleServiceUpdate}
                                        />
                                    </li>
                                );
                            })}
                        </ul>
                    )}
                </>
            }
        />
    );
};
